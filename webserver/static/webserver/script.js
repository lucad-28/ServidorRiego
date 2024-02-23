const time=100;
const url_ = "http://127.0.0.1:8000/webserver"     
var regando = "";

document.addEventListener('DOMContentLoaded', ()=>{
    console.log("document ready");
    setTimeout(updateHumedad,time);
    setTimeout(updateGota,time);
    setTimeout(rptProgramar,time);
    setTimeout(estadoRegadoProgramado,time);
});

const humDiv = document.getElementById('number');
const bar = document.getElementById('bar');
bar.style.strokeDashoffset = (100 - parseInt(humDiv.innerText))*660/100;

function updateHumedad(processHum){
    let xhr = new XMLHttpRequest();

    xhr.onreadystatechange = () => {
        if(xhr.readyState === 4 && xhr.status === 200){
            var humedad = xhr.responseText;
            var anterior = parseInt(humDiv.innerText);
            let counter = parseFloat(humDiv.innerText);

            setInterval(() =>{
                if(counter == humedad){
                    clearInterval;
                }else{
                    if(counter < humedad) counter += 1;
                    else if(counter > humedad) counter -= 1;
                    humDiv.innerText = `${counter}%`;
                    bar.style.strokeDashoffset = (100 - parseInt(humDiv.innerText))*660/100;
                }
            }, 20);
        }
    }

    xhr.open("GET", url_ + "/humedad");
    xhr.send();
    setTimeout(updateHumedad, time);
}

function onPressed(button) {
    let req = new XMLHttpRequest();
    if(button.checked)
        req.open("POST", url_ + "/regar?state=1",true);
    else
        req.open("POST", url_ + "/regar?state=0",true);
    req.send();
}

const gota = document.getElementById('gota');
const labelGota = document.getElementById('lGota');

function updateGota(processGota){
    let gotre = new XMLHttpRequest();

    gotre.onreadystatechange = () => {
        if(gotre.readyState === 4 && gotre.status === 200){
            
            var regadoForzado = gotre.responseText;
            console.log(regadoForzado);
            if(regadoForzado === "true"){
                gota.checked = true;
            }
            else if (regadoForzado === "false"){
                gota.checked = false;
            }
        }
    }

    gotre.open("GET", url_ + "/regar");
    gotre.send();
    setTimeout(updateGota, time);
}

function show(anything){
    document.querySelector('.textBox').value = anything;
}

let dropdown = document.querySelector('.dropdown');
dropdown.onclick = function(){
    dropdown.classList.toggle('active')
}

let flecha = document.querySelector('.flecha');
let formRegar = document.querySelector('.formRiego');

flecha.onclick = function(){
    formRegar.classList.add('Programado');
    var modo = document.getElementById('modoProgramado').textContent.toLowerCase().replace(" ","");
    var duracion = parseInt(document.getElementById('duracionRiego').value);
    var timer = document.getElementById('timer').value;
    console.log(String(modo) + " " + duracion + " " + timer);  
    /*
    var programado = {
        modalidad: modo,
        tiempo: duracion,
        unidad: timer
    };
    console.log("programado: ",programado)
    var datosEnviar = JSON.stringify(programado);
    console.log("datos a enviar", datosEnviar);
    */
    var soli= "via=escrito&"+"modo="+encodeURIComponent(modo)+"&duracion="+encodeURIComponent(duracion)+"&timer="+encodeURIComponent(timer);
    let programarR = new XMLHttpRequest();
    programarR.open("POST",url_ + "/rcomando?" + soli,true);
    //programarR.open("POST","/programar",true);
    /*
    programarR.setRequestHeader("Content-Type", "application/json");
    programarR.onload = function(){
        if (programarR.status >=200 && programarR.status < 300){
            console.log("Respuesta del servidor", programarR.responseText);
        }else{
            console.error("Error: ", programarR.statusText);
        }
    };
    */
    //programarR.send("plain=" + encodeURIComponent(datosEnviar));
    programarR.send();
}

let micro = document.querySelector('.microfono');
var comandoenviado = "";
const recognition = new webkitSpeechRecognition();

recognition.continuous = true;
recognition.lang = 'es-ES';
recognition.interimResult = false;

recognition.onresult = (event) => {
    const texto = event.results[event.results.length - 1][0].transcript;
    comandoenviado += texto;
    console.log(texto);
}

recognition.onerror = (event) => {
    console.log(`Speech recognition error detected: ${event.error}`);
    console.log(`Additional information: ${event.message}`);
};

micro.onclick = function(){
    micro.classList.toggle('grabando');
    if(micro.classList.contains('grabando')){
        console.log("iniciado");
        recognition.start();
        timeoutID = setTimeout(function(){
            if(micro.classList.contains('grabando')){
                micro.classList.toggle('grabando');
                console.log("Captura detenida por tiempo");
                recognition.stop();
                setTimeout(function(){
                    if(comandoenviado!=="" && comandoenviado){
                        console.log("comando enviado: " + comandoenviado)
                        enviarComando();
                    }
                },1000);
            }
        },6000);
    }else{
        console.log("terminado");
        recognition.stop();
        setTimeout(function(){
            if(comandoenviado!==""){
                console.log("comando enviado" + comandoenviado)
                enviarComando();
            }
        },1000);      
    }
}

function enviarComando(){
    let rcom = new XMLHttpRequest();
    rcom.open("POST", url_ + "/rcomando?contenido="+ comandoenviado);
    comandoenviado = "";
    rcom.send();
    
    formRegar.classList.add('Programado');
}

var mensajeProgramado = document.getElementById('MensajeProgramado');
function rptProgramar(processRpt){
    let rpt = new XMLHttpRequest();
    
    rpt.onreadystatechange = () => {
        if(rpt.readyState === 4 && rpt.status === 200){
            var Respuesta = rpt.responseText;
            console.log("rptProgramar");
            console.log(Respuesta);
            if(mensajeProgramado){
                
                if(Respuesta === "Esperando la respuesta del dispositivo"){
                    if(!formRegar.classList.contains('Programado')){
                        formRegar.classList.add('Programado');
                    }
                    mensajeProgramado.innerText = Respuesta;
                }else if(Respuesta === "Comando no reconocido"){
                    if(!formRegar.classList.contains('Programado')){
                        formRegar.classList.add('Programado');
                    }
                    mensajeProgramado.innerText = Respuesta;
                    setTimeout(function(){
                        formRegar.classList.remove('Programado');
                    },1000);
                }else if(Respuesta.includes("Se regara")){
                    if(!formRegar.classList.contains('Programado')){
                        formRegar.classList.add('Programado');
                    }
                    mensajeProgramado.innerText = Respuesta;
                }else if(Respuesta.includes("Se encenderan")){
                    if(!formRegar.classList.contains('Programado')){
                        formRegar.classList.add('Programado');
                    }
                    mensajeProgramado.innerText = Respuesta;
                }
            }else{
                mensajeProgramado = document.getElementById('MensajeProgramado');
            }
            
        }
    }

    rpt.open("GET", url_ + "/rptcomando");
    rpt.send();
    setTimeout(rptProgramar, time);
}

function estadoRegadoProgramado(processEst){
    let estado = new XMLHttpRequest();
    
    estado.onreadystatechange = () => {
        if(estado.readyState === 4 && estado.status === 200){
            var rpt = estado.responseText;
            if(rpt == "False" && (mensajeProgramado.innerText.includes("Se regara") || mensajeProgramado.innerText.includes("Se encenderan las luces"))){
                mensajeProgramado.innerText = "";
                formRegar.classList.remove('Programado');
            }
        }
    }
    estado.open("GET", url_ + "/riegoprog");
    estado.send();
    setTimeout(estadoRegadoProgramado, time);    
}