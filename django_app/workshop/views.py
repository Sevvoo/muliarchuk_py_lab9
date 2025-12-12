from django.shortcuts import render
from .models import Client, Car, Repair


def index(request):
    clients = Client.objects.all()
    cars = Car.objects.select_related('client').all()
    repairs = Repair.objects.select_related('car__client').all()
    
    context = {
        'clients': clients,
        'cars': cars,
        'repairs': repairs,
        'student_name': 'Мулярчук Сергій',
        'student_group': 'КН22002б',
    }
    
    return render(request, 'workshop/index.html', context)
