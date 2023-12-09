from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('login.html', views.login_view, name='login_view'),
    path('main.html', views.main, name="main"),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
]
