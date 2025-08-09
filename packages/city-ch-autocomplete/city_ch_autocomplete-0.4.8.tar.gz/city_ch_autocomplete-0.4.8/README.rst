city-ch-autocomplete
====================

city-ch-autocomplete is a Django helper app to add an autocomplete widget
in an address form that searches postal codes and locality names through the
post.ch API.

It depends on Bootstrap 5 to produce the autocomplete widget.

Quick start
-----------

1. Add "city_ch_autocomplete" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "city_ch_autocomplete",
    ]

2. Include city_ch_autocomplete urls to your urlpatterns::

    urlpatterns = [
        ...,
        path("", include("city_ch_autocomplete.urls")),
        ...,
    ]

2. Get an API access from the Swiss Post (starting from
   https://developer.apis.post.ch/ui/home). Note the process can take some
   time.
   Then add the POST_API_USER and POST_API_PASSWORD settings to your project.

   Optionally you can get the data from a CSV and put it in a database table.
   Read below for more details.

3. In the target form(s) of your project, add the `CityChMixin` to your
   form inheritance and a `CityChField` as a form field::

    from city_ch_autocomplete.forms import CityChField, CityChMixin

    class YourForm(CityChMixin, forms.ModelForm):
        class Meta:
            fields = [..., '<my_postcode_model_field>', '<my_city_model_field>', ...]
        city_auto = CityChField(...)
        postal_code_model_field = '<my_postcode_model_field>'
        city_model_field = '<my_city_model_field>'

   Don't forget to include `{{ form.media }}` in the templates where you are using
   the form.

Searching from the database
---------------------------

If for some reason, you would prefer searching postcodes/names from a database
table instead from the Swiss Post API, you can populate the `PLZdb` model with
external data. The `PLZdb.import_from_csv(csv_path)` class method allows for
importing such data.

A good CSV data source is https://www.swisstopo.admin.ch/fr/repertoire-officiel-des-localites
(choose the csv ending with `2056.csv`).

Then set the POST_API_USER setting to `None` and the view will search from the
database instead.

Geographic city filter
----------------------
If your database is spatially enabled, the `PLZdb.objects` manager allows for
searching cities from within a distance around another city::

    PLZdb.objects.filter_cities_around(<plz value>, <km>)
