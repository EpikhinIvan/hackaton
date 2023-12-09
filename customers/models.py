from django.db import models

class User(models.Model):
    driver_id = models.AutoField(primary_key=True)
    car_number = models.CharField(max_length=255)  # или другой максимальный размер, который вам нужен
    password = models.CharField(max_length=255)  # аналогично, выберите подходящую максимальную длину

    class Meta:
        db_table = 'users'  # Указание Django использовать существующую таблицу 'users'
        managed = False 

class Passenger(models.Model):
    passenger_id = models.AutoField(primary_key=True, default=0)
    flight_number = models.CharField(max_length=255)
    arrival_time = models.CharField(max_length=255)
    passenger_name = models.CharField(max_length=255)


class DriverPassengerRelation(models.Model):
    relation_id = models.AutoField(primary_key=True, default=0)
    car_number = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    passenger_name = models.ForeignKey(Passenger, on_delete=models.CASCADE, default='name')
    status = models.CharField(max_length=255)

  



   