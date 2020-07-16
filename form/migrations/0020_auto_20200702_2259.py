# Generated by Django 2.2 on 2020-07-02 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0019_sub_criteria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sub_criteria',
            name='Criteria_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sub_crits', to='form.Criteria', verbose_name='Критерий'),
        ),
        migrations.AlterModelTable(
            name='sub_criteria',
            table='sub_crits',
        ),
    ]