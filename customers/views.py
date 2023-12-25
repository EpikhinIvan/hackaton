from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Passenger, Driver
from .forms import DriverForm
from django.db.models import Count
import fitz
import re
from datetime import datetime
from .forms import UploadPDFForm
from django.http import HttpResponse
import logging
logger = logging.getLogger(__name__)

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
    else:
        form = DriverForm()

    return render(request, 'main/main.html', {'user': request.user, 'form': form})



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


##############################################

def extract_info(text):
    passenger_info_pattern = r"Passengers\s*SINGLE\s*([\w\s]+)\s*\("
    flight_info_pattern = r"(KC\d+),\s*(\d{2}\.\d{2}\.\d{4}\s*\(\d{2}:\d{2}\))"

    passenger_match = re.search(passenger_info_pattern, text)
    passenger_info = passenger_match.group(1) if passenger_match else 'Информация о пассажире не найдена'

    flight_info_matches = re.findall(flight_info_pattern, text)
    flight_info = flight_info_matches if flight_info_matches else 'Информация о рейсе не найдена'

    return passenger_info, flight_info

def filter_and_save(passenger_info, flight_info_list):
    for flight_info in flight_info_list:
        flight_number, flight_datetime = flight_info
        arrival_time = datetime.strptime(flight_datetime, '%d.%m.%Y (%H:%M)')

        for passenger_name in passenger_info.split('\n'):
            passenger_name = passenger_name.strip()
            if passenger_name:
                Passenger.objects.create(name=passenger_name, arrival_time=arrival_time, flight_number=flight_number)

def upload_pdf(request):
    if request.method == 'POST':
        form = UploadPDFForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['file']
            if pdf_file:
                try:
                    with fitz.open(stream=pdf_file.read(), filetype="pdf") as pdf:
                        pdf_text = ''
                        for page in pdf:
                            pdf_text += page.get_text()

                    passenger_info, flight_info = extract_info(pdf_text)

                    filter_and_save(passenger_info, flight_info)

                    return render(request, 'main/add_pas.html', {'form': form})
                except Exception as e:
                    logger.error(f'Ошибка при загрузке файла: {e}')
                    return HttpResponse(f'Error: {e}', status=500)
            else:
                return HttpResponse('Файл не был загружен.', status=400)
        else:
            return HttpResponse('Неверные данные формы.', status=400)
    else:
        form = UploadPDFForm()
        return render(request, 'main/add_pas.html', {'form': form})