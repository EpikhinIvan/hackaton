from django.db import models

class Driver(models.Model):
    car_number = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=[
        ('not_working', 'Не работает'),
        ('in_transit', 'В пути'),
        ('at_airport', 'В аэропорту'),
        ('picked_up', 'Забрал клиента')
    ], default='not_working')

    def __str__(self):
        return f'{self.car_number} - {self.status}'

class Passenger(models.Model):
    name = models.CharField(max_length=100)
    flight_number = models.CharField(max_length=20, default=0)
    arrival_time = models.CharField(max_length=40)
    assigned_driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    

    def __str__(self):
        return f'{self.name} - {self.arrival_time} - Assigned Driver: {self.assigned_driver}'
  



   