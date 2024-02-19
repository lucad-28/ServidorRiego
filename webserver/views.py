from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token

percenHum = 0
regarForzado = False
solicitudRegado = {
    'pendiente': False,
    'modo': "",
    'duracion': 0,
    'timer': ""
}
comando = {
    'recibido': False,
    'contenido': "",
    'respuesta': {
        'recibida': False,
        'valido': "",
    }
}

# Create your views here.
def index(request):
    global percenHum

    return render(request, "webserver/index.html", {
        'humedad': percenHum,
        'regarForzado': regarForzado,
        'regadoProgramado': comando['recibido']==True,
        'esperandoRespuesta': comando['recibido'] == True and comando['respuesta']['recibida'] == False
    })

@csrf_exempt
def humedad(request):
    global percenHum
    if request.method == 'POST':
        valor = request.GET.get('valor')
        valor_decimal = float(valor)
        percenHum = int(valor_decimal)
        return HttpResponse(str(percenHum), content_type="text/plain")
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
    global solicitudRegado, comando
    if request.method == 'POST':
        solicitudRegado['pendiente'] = True
        solicitudRegado['modo'] = request.GET.get('modo')
        solicitudRegado['duracion'] = request.GET.get('duracion')
        solicitudRegado['timer'] = request.GET.get('timer')
        comando['recibido'] = True
        comando['respuesta']['recibida'] = True
        print(f"{solicitudRegado}")
        return HttpResponse(f"{solicitudRegado['modo']}, {solicitudRegado['duracion']}, {solicitudRegado['timer']}", content_type="text/plain")
    elif request.method == 'GET':
        if comando['respuesta']['recibida'] == False and comando['recibido'] == True:
            comando['recibido'] = False
            comando['respuesta']['recibida'] = False
            solicitudRegado['pendiente'] = True
            return HttpResponse(f"{solicitudRegado['modo']}, {solicitudRegado['duracion']}, {solicitudRegado['timer']}", content_type="text/plain")
        else:
            return HttpResponse("No se encuentra programacion alguna", content_type = "text/plain")


@csrf_exempt
def rcomando(request):
    global comando
    if request.method == 'POST':
        comando['recibido'] = True
        if(request.GET.get('via')):
            comando['contenido'] = f"&{request.GET.get('modo')}, {request.GET.get('duracion')}, {request.GET.get('timer')}"
        else:
            comando['contenido'] = request.GET.get('contenido')
        print(f"Comando recibido: {comando['recibido']} y contenido {comando['contenido']}")
        return HttpResponse("Comando ingresado con exito", content_type ="text/plain")
    elif request.method == 'GET':
        if comando['recibido'] == True and comando['respuesta']['recibida'] == False:
            contenido = comando['contenido']
            return HttpResponse(f"{contenido}",content_type="text/plain")
        else:
            return HttpResponse("Comando no recibido", content_type="text/plain")
@csrf_exempt
def rptcomando(request):
    global comando, solicitudRegado
    if request.method == 'POST':
        comando['respuesta']['valido'] = request.GET.get('estado')
        comando['respuesta']['recibida'] = True
        if comando['respuesta']['valido'] == 'valido':
            return programar(request)
        elif comando['respuesta']['valido'] == "invalido":

            return HttpResponse("Comando no reconocido", content_type ="text/plain")
    elif request.method == 'GET':
        if comando['respuesta']['recibida'] == True and comando['recibido'] == True:
            comando['respuesta']['recibida'] = False
            if comando['respuesta']['valido'] == 'valido':
                return programar(request)
            elif comando['respuesta']['valido'] == "invalido":
                comando['recibido'] = False
                comando['contenido'] = ""
                comando['respuesta']['valido'] = ""
                comando['respuesta']['recibida'] = False
                solicitudRegado['pendiente'] == False
                return HttpResponse("Comando no reconocido", content_type ="text/plain")
        elif comando['respuesta']['recibida'] == False and comando['recibido'] == True:
            return HttpResponse("Respuesta aun no recibida del servidor", content_type="text/plain")
        elif solicitudRegado['pendiente'] == True:
            return HttpResponse(f"Se regara en {solicitudRegado['duracion']} {solicitudRegado['timer']}", content_type="text/plain")
        else:
            return HttpResponse("No hay comando pendiente", content_type="text/plain")

@csrf_exempt
def riegoprog(request):
    global solicitudRegado
    if request.method == 'POST':
        if request.GET.get('pendiente'):
            print(f"{request.GET.get('pendiente')}")
            solicitudRegado['pendiente'] = bool(request.GET.get('pendiente').lower() == "true")
        return HttpResponse(f"Solicitud pendiente cambiada a {solicitudRegado['pendiente']}",content_type="text/plain")
    elif request.method == 'GET':
        return HttpResponse(f"{solicitudRegado['pendiente']}", content_type="text/plain")