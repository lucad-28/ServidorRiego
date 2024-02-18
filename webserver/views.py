from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token

percenHum = 0
regarForzado = False
regadoProgramado = False
solicitudRegado = {
    "modo": "",
    "duracion": 0,
    "timer": ""
}

# Create your views here.
def index(request):
    global percenHum
   
    return render(request, "webserver/index.html", {
        'humedad': percenHum,
        'regarForzado': regarForzado
    })

@csrf_exempt
def humedad(request):
    global percenHum
    if request.method == 'POST':
        valor = request.GET.get('valor')
        percenHum = int(valor)
        return HttpResponse(f"Valor actualizado a {percenHum}", content_type="text/plain")
    elif request.method == 'GET':
        return HttpResponse(str(percenHum), content_type="text/plain")

@csrf_exempt
def regar(request):
    global regarForzado
    if request.method == 'POST':
        valor = request.GET.get('state')
        regarForzado = bool(int(valor))
        print(f"{regarForzado}, {valor}")
        return HttpResponse(f"Regar actualizado a: {regarForzado}", content_type="text/plain")
    elif request.method == 'GET':
        return HttpResponse(str(regarForzado).lower(), content_type="text/plain")

@csrf_exempt
def programar(request):
    global regadoProgramado, solicitudRegado
    if request.method == 'POST':
        solicitudRegado = request.GET
        regadoProgramado = True
        print(f"{solicitudRegado}")
        return HttpResponse(f"{solicitudRegado["modo"]}, {solicitudRegado["duracion"]}, {solicitudRegado["timer"]}", content_type="text/plain")
    elif request.method == 'GET':
        if regadoProgramado == True:
            return HttpResponse(f"{solicitudRegado["modo"]}, {solicitudRegado["duracion"]}, {solicitudRegado["timer"]}", content_type="text/plain")
        else:
            return HttpResponse("No se encuentra programacion alguna", content_type = "text/plain")