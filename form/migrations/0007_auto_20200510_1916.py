# Generated by Django 2.2 on 2020-05-10 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0006_auto_20200505_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='university_data',
            name='Value',
            field=models.FloatField(null=True),
        ),
    ]
