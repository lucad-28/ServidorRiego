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
comando = {
    "recibido": False,
    "contenido": "",
    "respuesta": {
        "recibida": False,
        "valido": False,
    }
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

@csrf_exempt
def rcomando(request):
    global comando
    if request.method == 'POST':
        comando["recibido"] = True
        comando["contenido"] = request.GET.get("contenido")
        print(f"Comando recibido: {comando['recibido']} y contenido {comando['contenido']}")
        return HttpResponse("Comando ingresado con exito", content_type ="text/plain")
    elif request.method == 'GET':
        if comando["recibido"] == True:
            comando["recibido"] = False
            contenido = comando["contenido"]
            return HttpResponse(f"{contenido}",content_type="text/plain")
        else:
            return HttpResponse("Comando no recibido", content_type="text/plain")
@csrf_exempt
def rptcomando(request):
    global comando
    if request.method == 'POST':
        comando["respuesta"]["estado"] = request.GET.get('estado')
        comando["respuesta"]["recibida"] = True
        if comando["respuesta"]["estado"] == "valido":
            return programar(request)
    elif request.method == 'GET':
        if comando["respuesta"]["recibida"] == True:
            comando["respuesta"]["recibida"] = False
            if comando["respuesta"]["valido"] == "valido":
                return programar(request)
            elif comando["respuesta"]["valido"] == "invalido":
                return HttpResponse("Comando no reconocido", content_type ="text/plain")
        else:
            return HttpResponse("Respuesta no recibida", content="text/plain")