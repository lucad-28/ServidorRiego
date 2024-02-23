from . import views
from django.urls import path

urlpatterns = [
    path("", views.index, name="index"),
    path("humedad", views.humedad, name="humedad"),
    path("regar", views.regar, name="regar"),
    path("programar", views.programar, name="programar"),
    path("rcomando",views.rcomando,name="comando"),
    path("rptcomando",views.rptcomando,name="rptcomando"),
    path("riegoprog", views.riegoprog, name="riegoprog"),
    path("encender", views.encender, name="encender")
]