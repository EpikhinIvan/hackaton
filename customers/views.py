from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .models import Passenger, Driver
from .forms import DriverForm
from django.db.models import Count


def index(request):
    results = None

    if request.method == 'POST':
        passenger_name = request.POST.get('passenger_name')
        if passenger_name:
            try:
                passengers = Passenger.objects.filter(name__icontains=passenger_name)
                results = [{'passenger': passenger, 'driver': passenger.assigned_driver} for passenger in passengers]
                print(results)

            except Passenger.DoesNotExist:
                print("No passengers found.")
            except Driver.DoesNotExist:
                print("No drivers found.")

    return render(request, 'main/index.html', {'results': results})



def main(request):
    return render(request, 'main/main.html')


def add_driver(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  
    return render(request, 'main/main.html', {'user': request.user, 'form': DriverForm()})


def login_view(request):
    error_message = None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            error_message = "Неправильный логин или пароль. Пожалуйста, попробуйте снова."

    return render(request, 'main/login.html', {'error_message': error_message})



def link_passenger_driver(request):
    if request.method == 'POST':
        passenger_id = request.POST.get('passenger_id')
        driver_id = request.POST.get('driver_id')

        passenger = Passenger.objects.get(pk=passenger_id)
        driver = Driver.objects.get(pk=driver_id)

        passenger.assigned_driver = driver
        passenger.save()

        return redirect('link_passenger_driver')

    passengers = Passenger.objects.filter(assigned_driver=None)
    drivers = Driver.objects.annotate(num_orders=Count('passenger__id'))
    
    return render(request, 'main/link_passenger_driver.html', {'passengers': passengers, 'drivers': drivers})
