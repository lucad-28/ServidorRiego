from . import views
from django.urls import path

urlpatterns = [
    path("", views.index, name="index"),
    path("humedad", views.humedad, name="humedad"),
    path("regar", views.regar, name="regar"),
    path("programar", views.programar, name="programar"),
    path("rcomando",views.rcomando,name="comando"),
    path("rptacomando",views.rptcomando,name="rptacomando")
]