# Generated by Django 2.2 on 2021-02-04 11:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0037_auto_20210204_1654'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student_form',
            name='major',
        ),
    ]
