# Generated by Django 3.0.7 on 2020-06-30 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('times', '0006_auto_20200630_2211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='pub_date',
            field=models.DateTimeField(null=True, verbose_name='date pubilshed'),
        ),
    ]