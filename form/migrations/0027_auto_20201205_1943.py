# Generated by Django 2.2 on 2020-12-05 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0026_student_form_year_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='student_form',
            name='own_spec',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='student_form',
            name='rating',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
