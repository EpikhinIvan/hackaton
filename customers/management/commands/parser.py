from django.core.management.base import BaseCommand
import requests
from datetime import datetime
from customers.models import Passenger

class Command(BaseCommand):
    help = 'Update passenger data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Updating passenger data...'))
        self.parse_and_update()

    def parse_and_update(self):
        response = requests.get('https://alaport.com/Home/getCurrentFlights?flightLeg=ARR&_=')
        data = response.json()

        for elements in data.get('data', {}).get('flights', []):
            airline_iata = elements.get('airlineIata')
            flight_number = elements.get('flightNumber')
            stad = elements.get('etad')

            try:
                passenger = Passenger.objects.get(flight_number=flight_number)
                arrival_time = datetime.strptime(stad, '%d.%m.%Y %H:%M')

                if passenger.arrival_time != arrival_time:
                    passenger.arrival_time = arrival_time
                    passenger.save()

                    self.stdout.write(self.style.SUCCESS(f'Airline IATA: {airline_iata} {flight_number}'))
                    self.stdout.write(self.style.SUCCESS(f'Stad: {stad} - Updated for passenger: {passenger}'))
            except Passenger.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Passenger with flight_number {flight_number} does not exist'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating passenger: {e}'))