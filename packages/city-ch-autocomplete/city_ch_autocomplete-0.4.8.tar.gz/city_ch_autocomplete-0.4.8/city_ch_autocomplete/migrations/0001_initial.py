from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='PLZdb',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID',
                )),
                ('name', models.CharField(max_length=50)),
                ('plz', models.CharField(max_length=4)),
            ],
            options={
                'indexes': [
                    models.Index(fields=['name'], name='common_plzd_name_f87817_idx'),
                    models.Index(fields=['plz'], name='common_plzd_plz_88d16d_idx')
                ],
            },
        ),
    ]
