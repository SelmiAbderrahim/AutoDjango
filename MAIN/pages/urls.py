from django.urls import path
from .views import home, add

urlpatterns = [
    path("", home, name="home"),
    path("add/", add, name="add"),
]