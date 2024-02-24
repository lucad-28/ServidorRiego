from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import re

percenHum = 0
regarForzado = False
encenderLuces = False
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
        'lucesForzadas': encenderLuces,
        'regadoProgramado': comando['recibido'] == True,
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
def encender(request):
    global encenderLuces
    if request.method == 'POST':
        valor = request.GET.get('state')
        encenderLuces = bool(int(valor))
        print(f"{encenderLuces}, {valor}")
        return HttpResponse(f"Encender actualizado a: {encenderLuces}", content_type="text/plain")
    elif request.method == 'GET':
        return HttpResponse(str(encenderLuces).lower(), content_type="text/plain")

@csrf_exempt
def programar(request):
    global solicitudRegado, comando
    if request.method == 'POST':
        solicitudRegado['pendiente'] = True
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
    global comando, solicitudRegado, encenderLuces, regarForzado
    if request.method == 'POST':
        comando['recibido'] = True
        comando['respuesta']['recibida'] = False
        if(request.GET.get('via')):
            comando['contenido'] = f"&{request.GET.get('modo')}, {request.GET.get('duracion')}, {request.GET.get('timer')}"
            solicitudRegado['modo'] = request.GET.get('modo')
            solicitudRegado['duracion'] = request.GET.get('duracion')
            solicitudRegado['timer'] = request.GET.get('timer')
        elif(request.GET.get('boton')):
            comando['contenido'] = f"&{request.GET.get('modo')}, 0, seg"
            solicitudRegado['modo'] = request.GET.get('modo')
            solicitudRegado['duracion'] = 0
            solicitudRegado['timer'] = "seg"
        else:
            mensaje = request.GET.get('contenido')

            modo, duracion, timer = examinar_mensaje(mensaje)
            solicitudRegado['modo'] = modo
            solicitudRegado['duracion'] = duracion
            solicitudRegado['timer'] = timer
            comando['contenido'] = f"{modo}, {duracion}, {timer}"
            if modo == "lucesInmediato":
                encenderLuces = True
                solicitudRegado['duracion'] = 0
                solicitudRegado['timer'] = 'seg'
                comando['contenido'] = f"{modo}, {solicitudRegado['duracion']}, {solicitudRegado['timer']}"
                return HttpResponse(f"Luces encendidas", content_type="text/plain")
            if modo == "regarInmediato":
                regarForzado = True
                solicitudRegado['duracion'] = 0
                solicitudRegado['timer'] = 'seg'
                comando['contenido'] = f"{modo}, {solicitudRegado['duracion']}, {solicitudRegado['timer']}"
                return HttpResponse(f"Regado iniciado", content_type="text/plain")

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
    global comando, solicitudRegado, regarForzado, encenderLuces
    if request.method == 'POST':
        comando['respuesta']['valido'] = request.GET.get('estado')
        comando['respuesta']['recibida'] = True
        if comando['respuesta']['valido'] == 'valido':
            return programar(request)
        elif comando['respuesta']['valido'] == "invalido":
            return HttpResponse("Comando no reconocido", content_type ="text/plain")
    elif request.method == 'GET':
        if comando['respuesta']['recibida'] == True and comando['recibido'] == True:
            if comando['respuesta']['valido'] == 'valido':
                if(solicitudRegado['modo'] == "regaren"):
                    return HttpResponse(f"Se regara en {solicitudRegado['duracion']} {solicitudRegado['timer']}", content_type="text/plain")
                elif(solicitudRegado['modo'] == 'lucesen'):
                    return HttpResponse(f"Se encenderan las luces en {solicitudRegado['duracion']} {solicitudRegado['timer']}", content_type="text/plain")
                elif(solicitudRegado['modo'] == 'lucesInmediato'):
                    return HttpResponse(f"Se encenderan las luces", content_type="text/plain")
                elif(solicitudRegado['modo'] == "regarInmediato"):
                    return HttpResponse(f"Se regara de inmediato", content_type="text/plain")
                elif(solicitudRegado['modo'] == "apagarregadoInmediato"):
                    return HttpResponse(f"Se apagara el regado de inmediato", content_type="text/plain")
                elif(solicitudRegado['modo'] == "apagarlucesInmediato"):
                    return HttpResponse(f"Se apagaran las luces de inmediato", content_type="text/plain")

            elif comando['respuesta']['valido'] == "invalido":
                comando['recibido'] = False
                comando['contenido'] = ""
                comando['respuesta']['valido'] = ""
                comando['respuesta']['recibida'] = False
                solicitudRegado['pendiente'] = False
                return HttpResponse("Comando no reconocido", content_type ="text/plain")
        elif comando['respuesta']['recibida'] == False and comando['recibido'] == True:
            return HttpResponse("Esperando la respuesta del dispositivo", content_type="text/plain")
        else:
            return HttpResponse("No hay comando pendiente", content_type="text/plain")

@csrf_exempt
def riegoprog(request):
    global solicitudRegado, regarForzado, encenderLuces, comando
    if request.method == 'POST':
        if request.GET.get('pendiente'):
            print(f"{request.GET.get('pendiente')}")
            solicitudRegado['pendiente'] = bool(request.GET.get('pendiente').lower() == "true")
            comando['recibido'] = False
            comando['contenido'] = ""
            comando['respuesta']['valido'] = ""
            comando['respuesta']['recibida'] = False
            solicitudRegado['pendiente'] = False
            if(solicitudRegado['modo'] == "regaren" or solicitudRegado['modo'] == "regarInmediato"):
                regarForzado = True
            elif(solicitudRegado['modo'] == "apagarregadoInmediato"):
                regarForzado = False
            elif(solicitudRegado['modo'] == "lucesInmediato" or solicitudRegado['modo'] == "lucesen"):
                encenderLuces = True
            elif(solicitudRegado['modo'] == "apagarlucesInmediato"):
                encenderLuces = False
        return HttpResponse(f"Solicitud pendiente cambiada a {solicitudRegado['pendiente']}",content_type="text/plain")
    elif request.method == 'GET':
        return HttpResponse(f"{solicitudRegado['pendiente']}", content_type="text/plain")

def examinar_mensaje(mensaje):

    # Patrón de expresión regular para buscar la palabra clave, el número y la unidad de tiempo

    patronregar = r'(enc(?:iende|ender)|activ(?:a|ar|es)|prend(?:e|er|as))\s+?(?:el sistema|sistema|el regado|regado)\s+(?:en|dentro de)\s+(\d+)\s+(segundos?|minutos?|horas?)'
    patronregarInmediato = r'(enc(?:iende|ender)|activ(?:a|ar|es)|prend(?:e|er|as))\s+?(?:el sistema?|sistema?|el regado?|regado?)$'
    patronluz = r'(enc(?:iende|ender)|activ(?:a|ar|es)|prend(?:e|er|as))\s+?(?:las luces|luces|la luz|el led)\s+(?:en|dentro de)\s+(\d+)\s+(segundos?|minutos?|horas?)'
    patronluzInmediato = r'(enc(?:iende|ender)|activ(?:a|ar|es)|prend(?:e|er|as))\s+?(?:las luces?|luces?|la luz?|el led?)$'

    # Buscar coincidencias en el mensaje
    coincidencias = re.search(patronregar, mensaje, re.IGNORECASE)
    modo = ""
    numero = 0
    unidad_tiempo = ""

    if coincidencias:
        palabra_clave = coincidencias.group(1)
        numero = int(coincidencias.group(2))
        unidad_tiempo = coincidencias.group(3)
        modo = "regaren"
    else:
        coincidencias = re.search(patronluz, mensaje, re.IGNORECASE)
        if coincidencias:
            palabra_clave = coincidencias.group(1)
            numero = int(coincidencias.group(2))
            unidad_tiempo = coincidencias.group(3)
            modo = "lucesen"
        else:
            coincidencias = re.search(patronluzInmediato, mensaje, re.IGNORECASE)
            if coincidencias:
                modo = "lucesInmediato"
                numero = None
                unidad_tiempo = None
            else:
                coincidencias = re.search(patronregarInmediato, mensaje, re.IGNORECASE)
                if coincidencias:
                    modo = "regarInmediato"
                    numero = None
                    unidad_tiempo = None
                else:
                    modo = None
                    numero = None
                    unidad_tiempo = None


    return modo, numero, unidad_tiempo

