from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


def index(request):
    return render(request, 'main/index.html')


def main(request):
    return render(request, 'main/main.html')


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