# Generated by Django 2.2 on 2020-12-05 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0029_student_form_networking'),
    ]

    operations = [
        migrations.AddField(
            model_name='student_form',
            name='own_skills',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
