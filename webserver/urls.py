from . import views
from django.urls import path

urlpatterns = [
    path("", views.index, name="index"),
    path("humedad", views.humedad, name="humedad"),
    path("regar", views.regar, name="regar")
]