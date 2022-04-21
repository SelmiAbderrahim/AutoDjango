from django.shortcuts import render
from .models import Film
from django.http import HttpResponse

def home(request):
    films = Film.objects.all()
    return render(request, "home1.html", {
        "films":films
    })

def add(request):
    query = request.GET.get("film")
    Film.objects.create(name=query)
    films = Film.objects.all()
    return render(request, "films.html", {
        "films":films
    })