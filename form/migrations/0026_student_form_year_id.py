# Generated by Django 2.2 on 2020-11-30 08:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0025_auto_20201121_1954'),
    ]

    operations = [
        migrations.AddField(
            model_name='student_form',
            name='Year_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='form.Year', verbose_name='Год'),
        ),
    ]