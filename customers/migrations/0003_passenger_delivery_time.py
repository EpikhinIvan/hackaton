# Generated by Django 4.2.7 on 2023-12-24 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_passenger_flight_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='passenger',
            name='delivery_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]