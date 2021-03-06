# Generated by Django 2.2 on 2021-01-13 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0031_emp_form'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dig_form',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('printer', models.IntegerField()),
                ('office', models.IntegerField()),
                ('sm', models.IntegerField()),
                ('internet', models.IntegerField()),
                ('trust', models.IntegerField()),
                ('portal', models.IntegerField()),
                ('card', models.IntegerField()),
                ('purchase', models.IntegerField()),
                ('online', models.IntegerField()),
                ('promotion', models.IntegerField()),
                ('rid', models.IntegerField()),
                ('encapsulation', models.IntegerField()),
                ('language', models.IntegerField()),
                ('program_lang', models.IntegerField()),
                ('telemedicine', models.IntegerField()),
                ('University_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='form.University', verbose_name='Университет')),
            ],
        ),
    ]
