from django import forms
from .models import Driver

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['car_number', 'password']

class UploadPDFForm(forms.Form):
    file = forms.FileField(label='Выберите файл PDF')



