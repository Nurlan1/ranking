# Generated by Django 2.2 on 2020-05-15 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0014_auto_20200514_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='criteria',
            name='VariableName',
            field=models.TextField(blank=True, null=True),
        ),
    ]
