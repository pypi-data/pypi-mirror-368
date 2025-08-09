from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('city_ch_autocomplete', '0001_initial'),
    ]

    operations = [
        migrations.RenameIndex(
            model_name='plzdb',
            new_name='plzdb_name_idx',
            old_name='common_plzd_name_f87817_idx',
        ),
        migrations.RenameIndex(
            model_name='plzdb',
            new_name='plzdb_plz_idx',
            old_name='common_plzd_plz_88d16d_idx',
        ),
    ]
