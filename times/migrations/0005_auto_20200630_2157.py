# Generated by Django 3.0.7 on 2020-06-30 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('times', '0004_auto_20200630_1926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='time_entry',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6),
        ),
    ]