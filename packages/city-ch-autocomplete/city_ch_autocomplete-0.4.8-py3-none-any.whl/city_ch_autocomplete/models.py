import csv

from django.apps import apps
from django.contrib.gis.measure import Distance as D
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models import Value as V
from django.db.models.functions import Concat

if apps.is_installed("django.contrib.gis"):
    from django.contrib.gis.db.models.functions import FromWKT
else:
    FromWKT = None


class PLZdbManager(models.Manager):
    def with_point(self):
        if FromWKT is None:
            raise NotImplementedError(
                "Unable to annotate with point when django.contrib.gis is not installed"
            )
        return self.annotate(
            point=FromWKT(
                Concat(V("POINT ("), "coord_x", V(" "), "coord_y", V(")"), output_field=models.CharField),
                srid=2056,
            )
        )

    def filter_cities_around(self, plz, km):
        center_city = PLZdb.objects.with_point().filter(plz=plz).first()
        if center_city is None:
            raise ObjectDoesNotExist(f"No PLZdb instance with plz={plz}")
        return PLZdb.objects.with_point().filter(point__dwithin=(center_city.point, D(km=km)))


class PLZdb(models.Model):
    """Model to optionally store city/postcodes in the database."""
    name = models.CharField(max_length=50)
    plz = models.CharField(max_length=4)
    # Coordinates of the city center, in SRID 2056 (LV95)
    # Not using PointField to not depend on django.contrib.gis being installed.
    coord_x = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    coord_y = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    objects = PLZdbManager()

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='plzdb_name_idx'),
            models.Index(fields=['plz'], name='plzdb_plz_idx'),
        ]

    def __str__(self):
        return f"{self.plz} {self.name}"

    @classmethod
    def import_from_csv(cls, csv_path, encoding="utf-8-sig", with_coords=True):
        """
        The CSV file is supposed to come from:
        https://www.swisstopo.admin.ch/fr/repertoire-officiel-des-localites
        (ortschaftenverzeichnis_plz_2056.csv)
        """
        with transaction.atomic():
            PLZdb.objects.all().delete()
            with open(csv_path, encoding=encoding) as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    # Using get_or_create to avoid doubles
                    PLZdb.objects.get_or_create(
                        name=row["Ortschaftsname"], plz=row["PLZ"],
                        defaults={"coord_x": row["E"], "coord_y": row["N"]} if with_coords else {}
                    )
