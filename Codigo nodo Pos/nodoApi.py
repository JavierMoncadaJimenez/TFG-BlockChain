from flask import Flask, request
import requests
from hashlib import sha256
import json
import time
import random
import configparser
import threading
import random

from blockchain import Blockchain
from Block import Block

blockchain = None

app = Flask(__name__)


config_file = configparser.ConfigParser()
config_file.read("configuracionNodo.ini")

puerto = config_file["Nodo"]["puerto"]
controlador = "http://" + config_file["Nodo"]["controlador"] + ":" + config_file["Nodo"]["puertoControlador"]+"/"
tarjetaRed = config_file["Nodo"]["tarjetaRed"]
nombre = config_file["Nodo"]["nombre"]
url = "http://{0}/{1}"

nodos = {}
tiempoNodo = int(config_file["Nodo"]["tiempo"]);

#Mensajes de error comunes en los metodos
MENSAJE_NO_CONFIGURADO="El nodo no esta configurado"
MENSAJE_NO_CENTRAL= "No se encuentra el nodo central"

"""
Interfaz del API que devuelve el nombre del nodo
"""
@app.route('/nombre', methods=['GET'])
def getNombre():
    return nombre, 201

"""
Interfaz del API que devuelve la cadena de bloques que tiene el nodo.
"""
@app.route('/cadena', methods=['GET'])
def get_chain():
    if not blockchain:
        return MENSAJE_NO_CONFIGURADO, 401
    
    chain_data = []
    
    for block in blockchain.cadena:
        chain_data.append(block.__dict__)

    return json.dumps({"logitud": len(chain_data),
                       "cadena": chain_data}), 201

"""
Interfaz que se utilizar para poder conectar el nodo a la red, cada vez que se crea el nodo se tiene que aceder a esta ruta
para configurar correctamente el nodo.
"""
@app.route('/', methods=['GET'])
def conf_nodo():
    global blockchain
    try:
        datosR = requests.get(controlador + "nodos").json()["nodos"]
        blockchain = Blockchain()
    except requests.exceptions.ConnectionError as e:
        return MENSAJE_NO_CENTRAL, 401

    
    nodo = {"direccion":(tarjetaRed + ":" + puerto),"nombre":nombre, "tiempo":tiempoNodo}   
    
    if nodo in datosR:
        return "Nodo ya conectado", 401
    
    for n in datosR: 
        nodos[n["direccion"]] = n["nombre"]
     
    requests.post(controlador + "nodo_nuevo",json=nodo)
    
    if len(datosR) > 0:
        dirNodo = url.format(datosR[0]["direccion"], "cadena")
        bloques = requests.get(dirNodo).json()["cadena"];

        for bloque in bloques:
            b = Block(indice=bloque["indice"], datos=bloque["datos"], timestamp=bloque["timestamp"], hash_previo=bloque["hash_previo"])
            b.nonce=bloque["nonce"]
            b.hash=bloque["hash"]
            blockchain.cadena.append(b)
        
        actulizarTransacciones()
    else:
        blockchain.crearBloqueGenesis()
    
    
    hilo = threading.Thread(target=actualizarTiempo)
    hilo.setDaemon(True)
    hilo.start()
        
    return "Nodo creado y añadido a la red", 201
    
"""
Interfaz para poder hacer que el nodo mine los bloques pendientes.
La funcionalidad de este metodo es la siguiente:
    -Primero solicita al nodo controlador el siguiente bloque que necesita ser minado.
    -Segundo el nodo mina el bloque, es decir, busca el hash correcto
    -Tercero se lo manda al nodo controlador para que este lo valide.
"""
@app.route('/minar', methods=['GET'])
def minarNodo():
    if not blockchain:
        return MENSAJE_NO_CONFIGURADO, 401
    
    if nodos: #Se evalua como false el diccionario vacio
        dirNodo = url.format(list(nodos.keys())[0], "minarBloque")
    else:
        dirNodo = url.format(tarjetaRed+":"+puerto, "minarBloque")

    try:
        bloquesMinar = requests.get(dirNodo).json()["transaccion"]
    except requests.exceptions.ConnectionError as e:
        return "Error al obtener los bloques pendientes de minar", 401
    
    if not bloquesMinar:
        return "No hay bloques para minar", 401
        
    b = bloquesMinar [0]
    b = Block(b["indice"], "Bloque solicitado por " + b["autor"] + ' con contenido: "'+ b["contenido"] + '" minado por ' + nombre, b["timestamp"], blockchain.ultimoBloque.hash)
    b.hash = b.calcularHash()
        
    positivos = 0
        
    for nodo in nodos.keys():
        dirNodo = url.format(nodo, "validar")
        r = requests.post(dirNodo,json=b.__dict__) 
        if r.status_code == 201:
            positivos = positivos + 1
                
    if positivos == len(nodos.keys()):
        for n in nodos:
            dirNodo = url.format(n, "nuevo_bloque")
            r = requests.post(dirNodo,json=b.__dict__)
            
        proof = b.hash
        blockchain.nuevoBloque(b, proof)

        return b.__dict__, 201
    else:
        return "El bloque no es valido", 401

"""
Interfaz que devuelve los nodos que hay en la red.
Devulve los datos en formato json, el primer parametros es la cantidad de nodos que hay.
El segundo parametro es la lista de nodos.
"""
@app.route('/nodos', methods=['GET'])
def getNodos():
    datos_cadena = []
    for nodo in nodos:
        datos_cadena.append({"direccion":nodo, "nombre":nodos[nodo][0], "tiempo":nodos[nodo][1]})
    return json.dumps({"logitud": len(datos_cadena),
                       "nodos": datos_cadena})


"""
Interfaz para añadir nuevos nodos
Esta interfaz es llamada por el controlador cuando se conecta un nuevo nodo.
Cuando recibe la peticion, el nodo pide la lista de nodo y la actualiza.
"""
@app.route('/nodo_nuevo', methods=['GET'])
def registrarNuevoNodo():
    try:
        datosR = requests.get(controlador + "nodos").json()["nodos"]
    except requests.exceptions.ConnectionError as e:
        return MENSAJE_NO_CENTRAL, 401
    
    ruta = tarjetaRed + ":" + puerto
    
    nodos.clear()
    
    for nodo in datosR:
        if (nodo["direccion"] != ruta):
            nodos[nodo["direccion"]] = [nodo["nombre"], nodo["tiempo"]]

    return "Operacion realizada con exito", 201
    
"""
Interfaz para poder añadir un nuevo bloque minado por los nodos.
Este bloque es validado por el nodo y si es correcto, lo añade a la red
y anuncia a los demas nodos que se ha añadido un nuevo bloque.
"""
@app.route('/nuevo_bloque', methods=['POST'])
def anidirBloque():
    if not blockchain:
        return MENSAJE_NO_CONFIGURADO, 401
    
    datos_bloque = request.get_json()
    bloque = Block(datos_bloque["indice"],
                  datos_bloque["datos"],
                  datos_bloque["timestamp"],
                  datos_bloque["hash_previo"])

    proof = datos_bloque["hash"]
    bloque.nonce = datos_bloque["nonce"]
    
    aniadido = blockchain.nuevoBloque(bloque, proof)
    
    if not aniadido:
        return "El bloque ha sido rechazado por el nodo", 401
    
    return "Bloque añadido a la cadena", 201
    

"""
Interfaz para poder actualizar la lista de nuevos bloques para que los nodos de la red los validen
"""
@app.route('/actualizarTransaccion', methods=['POST'])
def atualizarTransaccion():
    tx_datos = request.get_json()
    campos = ["autor", "contenido","timestamp"]

    for campo in campos:
        if not tx_datos.get(campo):
            return "Datos invalidos", 400


    blockchain.aniadirNuevaTransacción(tx_datos)
    return "Operacion realizada con exito", 201
    
"""
Interfaz para poder validar el bloque mandado por otros nodos.
"""
@app.route('/validar', methods=['POST'])
def validarBloque():
    if not blockchain:
        return MENSAJE_NO_CONFIGURADO, 401
    
    datos_bloque = request.get_json()
    bloque = Block(datos_bloque["indice"],
                  datos_bloque["datos"],
                  datos_bloque["timestamp"],
                  datos_bloque["hash_previo"])

    proof = datos_bloque["hash"]
    bloque.nonce = datos_bloque["nonce"]
    aniadido = blockchain.validar(bloque=bloque, proof=proof)
    
    if not aniadido:
        return "El bloque no es valido", 401
    
    return "El bloque es valido", 201

"""
Función que anuncia a los nodos unidos a la red que se a actulizado la cadena de bloques.
Esta funcion hace una peticion POST a todos los nodos, y les manda el bloque nuevo que tienen que añadir
"""                       
def anunciarNuevoBloque(bloque):
    for nodo in nodos.keys():
        dirNodo = url.format(nodo, "nuevo_bloque")
        requests.post(dirNodo, json=bloque.__dict__)

"""
Interfaz del API para poder añadir nuevos bloques a la lista de espera para que los nodos de la red los validen
"""
@app.route('/nueva_transaccion', methods=['POST'])
def nuevaTransaccion():
    if not blockchain:
        return MENSAJE_NO_CONFIGURADO, 401
    
    tx_datos = request.get_json()
    campos = ["autor", "contenido"]

    for campo in campos:
        if not tx_datos.get(campo):
            return "Datos invalidos", 401

    tx_datos["timestamp"] = time.time()
    
    
    votos = pedirVoto()
    
    if votos:
        ganador = max(votos,key=votos.count)
    else:
        ganador=tarjetaRed + ":" + puerto + "/" 
    
    blockchain.aniadirNuevaTransacción(tx_datos)
    anunciarNuevaTransaccion(tx_datos)
    
    dirNodo = url.format(ganador, "minar")
    requests.get(dirNodo, json=tx_datos)
    return ganador, 201

"""
Función que realizar las peticiones a los nodos de la red para preguntarles que nodo tiene que minar el bloque.
"""
def pedirVoto():
    votos = []
    
    for nodo in nodos:
        dirNodo = url.format(nodo, "voto")
        r = requests.get(dirNodo).json()["ganador"]
        votos.append(r)
    
    return votos

"""
Interfaz del API que ofrece el nodo que deveria validar el nuevo bloque
"""
@app.route('/voto', methods=['GET'])
def obtenerVoto():
    validadores = []
    nodosCopia = nodos.copy()
    nodosCopia[tarjetaRed + ":" + puerto] = [nombre, tiempoNodo]
    
    for nodo in nodosCopia.keys():
        tiempo = nodosCopia[nodo][1]
        for i in range(int(tiempo)):
            validadores.append(nodo)
    
    ganador = random.choice(validadores)
    return {"ganador":ganador}, 201

"""
Función que avisa a todos los nodos de la red de que se ha añadido un nuevo bloque a minar.
"""
def anunciarNuevaTransaccion(tx):
    for nodo in nodos:
        dirNodo = url.format(nodo, "actualizarTransaccion")
        requests.post(dirNodo, json=tx)
    
"""
Interfaz que devuelve los bloques que hay que minar.
Devulve los datos en formato json, el primer parametros es la cantidad de bloques que hay.
El segundo parametro es la lista de nodos.
"""
@app.route('/minarBloque', methods=['GET'])
def bloquesMinar():
    if not blockchain:
        return MENSAJE_NO_CONFIGURADO, 401
    
    datosCadena = []
    for bloque in blockchain.transaccionSinConfirmar:
        bloque["indice"] = blockchain.ultimoBloque.indice + 1
        datosCadena.append(bloque)
    return json.dumps({"logitud": len(datosCadena),
                       "transaccion": datosCadena})

"""
Función que se encarga de incrementar el tiempo de cada nodo vecino y el tiempo del mismo nodo.
"""                       
def incrementarTiempo():
    registrarNuevoNodo()
    
    global tiempoNodo
    tiempoNodo = tiempoNodo + 1
    
"""
Función que actualiza las transacciones del nodo, este metodo se ejecuta cuano el nodo se conecta
"""
def actulizarTransacciones():
    dirNodo = url.format(list(nodos.keys())[0], "minarBloque")

    transacciones = requests.get(dirNodo).json()["transaccion"]

    for transaccion in transacciones:
        blockchain.aniadirNuevaTransacción(transaccion)

"""
Función para incrementar el tiempo de los ndoos. Es la función pricipal, es decir, esta es la que se ejecutará en un hilo
y controlará dicho hilo.
"""
def actualizarTiempo():
    while(True):
        time.sleep(60)
        incrementarTiempo()

"""
Interfaz para recibir la peticion para poder desconectar el nodo de la red.
Para realizar esto, se manda los datos del nodo al controlador y se reinica el objeto de la blockchain
para desconfigurarlo correctamente.
"""
@app.route('/desconectar', methods=['GET'])
def desconectarNodo():
    try:
        nodo = {"direccion": (tarjetaRed + ":" + puerto),"nombre":nombre}
        respuesta = requests.post(controlador + "desconectar_nodo",json=nodo)
        respuesta.raise_for_status()

        global blockchain
        blockchain = None

        return "El nodo se ha desconectado", 201
    
    except requests.exceptions.HTTPError as e:
        if e.request.status_code == 401:
            return e.request.text, 401
    except requests.exceptions.ConnectionError as e:
        return MENSAJE_NO_CENTRAL, 401

app.run(debug=False, port=int(puerto), host=tarjetaRed)



