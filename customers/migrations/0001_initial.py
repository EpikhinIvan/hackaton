# Generated by Django 4.2.7 on 2023-12-09 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('driver_id', models.AutoField(primary_key=True, serialize=False)),
                ('car_number', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'users',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('passenger_id', models.AutoField(default=0, primary_key=True, serialize=False)),
                ('flight_number', models.CharField(max_length=255)),
                ('arrival_time', models.CharField(max_length=255)),
                ('passenger_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='DriverPassengerRelation',
            fields=[
                ('relation_id', models.AutoField(default=0, primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=255)),
                ('car_number', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='customers.user')),
                ('passenger_name', models.ForeignKey(default='name', on_delete=django.db.models.deletion.CASCADE, to='customers.passenger')),
            ],
        ),
    ]