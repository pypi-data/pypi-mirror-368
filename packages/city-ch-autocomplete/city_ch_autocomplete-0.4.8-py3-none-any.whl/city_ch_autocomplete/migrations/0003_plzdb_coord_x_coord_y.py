from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('city_ch_autocomplete', '0002_rename_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='plzdb',
            name='coord_x',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='plzdb',
            name='coord_y',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True),
        ),
    ]
