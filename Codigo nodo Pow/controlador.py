from flask import Flask, request
import requests
from hashlib import sha256
import json
import configparser

app = Flask(__name__)
# Contiene la direccion de cada uno de los nodos conectados a la red
nodos = {}

archivoConfiguracion = configparser.ConfigParser()
archivoConfiguracion.read("configuracionNodo.ini")

tarjetaRed = archivoConfiguracion["Controlador"]["tarjetaRed"]
puerto = archivoConfiguracion["Controlador"]["puerto"]


"""
Interfaz para añadir nuevos nodos
Se le tiene que pasar por medio de una peticion post los siguientes datos:
    -address => ip del nodo
    -nombre => el nombre que se le ha dado al nodo.
Estos datos tienen que darse en forma de json
"""
@app.route('/nodo_nuevo', methods=['POST'])
def registrarNuevoNodo():
    nodo = request.get_json()
    if not nodo:
        return "Invalid data", 401
        
    direccion = nodo.get("direccion")
    nombre = nodo.get("nombre")
    nodos[direccion] = nombre
    
    anunciarNuevoNodo()
    return "Operacion realizada con exito", 201

"""
Metodo que se encarga de avisar a los demas nodos que se ha cambiado
la lista de nodos, ya sea porque se ha unido un nuevo nodo o se ha
desconectado un nodo.
"""
def anunciarNuevoNodo ():
    for nodo in nodos:
        url = "http://{}/nodo_nuevo".format(nodo)
        requests.get(url)

"""
Punto de la interfaz para poder gestionar la desconexion de los nodos.
Lo que hace es eliminarlo de lista de nodos y avisar a la red que se ha
modificado dicha lista.
"""
@app.route('/desconectar_nodo', methods=['POST'])
def desconectarNodo():
    nodo = request.get_json()
    
    if not nodo:
        return "Invalid data", 401
        
    direccion = nodo.get("direccion")
    nombre = nodo.get("nombre")
    
    if not direccion in nodos:
        return "El nodo ya esta desconectado", 401
    
    del nodos[direccion] 

    anunciarNuevoNodo()
    return "Operacion realizada con exito", 201

"""
Interfaz que devuelve los nodos que hay en la red.
Devulve los datos en formato json, el primer parametros es la cantidad de nodos que hay.
El segundo parametro es la lista de nodos.
"""
@app.route('/nodos', methods=['GET'])
def obtenerNodos():
    datos_cadena = []
    for nodo in nodos:
        datos_cadena.append({"direccion":nodo, "nombre":nodos[nodo]})
    return json.dumps({"logitud": len(datos_cadena),
                       "nodos": datos_cadena})

"""
Punto de la interfaz que devuelve la dificultad de minar un bloque en la red.
"""
@app.route('/dificultad', methods=['GET'])
def obtenerDificultad():
    dificultad = archivoConfiguracion["Blockchain"]["dificultad"]
    return dificultad, 201
                      

app.run(debug=False, port=puerto, host=tarjetaRed)