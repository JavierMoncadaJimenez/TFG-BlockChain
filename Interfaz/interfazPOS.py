from tkinter import *
import os
import requests
import threading
from configparser import ConfigParser
from interfazAniadirTrans import *
from datetime import datetime
from Tooltip import Tooltip

class InterfazPos():
    """Contructor del objeto. Carga el archivo de configuración y los colores usables."""
    def __init__(self, numNodos):
        self.conf = ConfigParser()
        self.conf.read("dirNodos.ini")
        self.numNodosConectados = 0
        self.colores = ["forestgreen", "blueviolet", "skyblue", "chocolate", "orange"]
        self.construirVentana(numNodos)
    
    """Métdo para crear todos los elementos de la interfaz"""
    def construirVentana(self, numNodos):
        self.window= Tk()
        self.window.resizable(False, False)
        self.window.title('Blockchain POW')
        self.estados = [False]
        self.botones = []

        for i in range (numNodos - 1):
            self.estados.append(False)
        
        #Frame botones controlador y nodos
        self.arribaFrame = Frame()
        self.arribaFrame.grid(row=1,column=0)

        #Control para el controlador
        self.controladorGB = LabelFrame(self.arribaFrame, text="Nodo controlador", font=("Arial", 14))
        self.controladorGB.grid(row=0,column=0, padx=30, pady=30)
        
        
        self.controlNCFrame = Frame(self.controladorGB)
        self.controlNCFrame.grid(row=0, column=0)

        self.infoConsensoLb = Label(self.controlNCFrame, text="Consenso de la red: POS", font=("Arial", 12))
        self.infoConsensoLb.grid(row=0, column=0)

        self.infoNodosAniadidos = Label(self.controlNCFrame, text="Nodos añadidos a la red: " + str(numNodos), font=("Arial", 12))
        self.infoNodosAniadidos.grid(row=1, column=0)
        
        self.infoNodosConectado = Label(self.controlNCFrame, text="Nodos conectados a la red: " + str(self.numNodosConectados), font=("Arial", 12))
        self.infoNodosConectado.grid(row=2, column=0)

        fila=0
        columna = 1
        
        for i in range(1, numNodos + 1):
            nombre = self.obtenerNombre(str(i))
            nodoGB = LabelFrame(self.arribaFrame, text=nombre, font=("Arial", 14), fg=self.colores[i - 1])
            nodoGB.grid(row=fila,column=columna, padx=30, pady=30)

            nodo=str(i)
            conectarNbtn = Button(nodoGB, text="Conectar", command = lambda n=nodo: threading.Thread(target=self.controlarBoton, args=(n)).start())
            conectarNbtn.grid(row=1, column=0, padx=10)
            Tooltip(conectarNbtn, "Botón para conectra y desconectar el nodo")
            self.botones.append(conectarNbtn)

            cadenaNbtn = Button(nodoGB, text="Visualizar", command= lambda n=nodo: threading.Thread(target=self.cadenaDeBloques, args=(n)).start())
            Tooltip(cadenaNbtn, "Botón para visualizar los bloques del nodo")
            cadenaNbtn.grid(row=0, column=1, padx=(0,10))

            visaalizarNbtn = Button(nodoGB, text="Añadir", command= lambda nom=nombre: threading.Thread(target=self.aniadirTransaccion, args=(nom,numNodos)).start())
            Tooltip(visaalizarNbtn, "Botón para poder añadir un nuevo bloque a la lista de pendientes de ser minados")
            visaalizarNbtn.grid(row=1, column=1)

            columna = columna + 1

            if columna > 1:
                fila = fila + 1
                columna = 0
            
        #Frame para la consola de los nodos
        self.abajoFrame = Frame()
        self.abajoFrame.grid(sticky="W", row=3,column=0, pady=20,padx=10)

        #Consola de los nodos
        self.consolaFrame = Frame(self.abajoFrame)

        self.consolaLb = Label(self.consolaFrame, text="Consola de los nodos", font=("Arial", 14),anchor="w")
        self.consolaLb.grid(sticky="W",row=0,column=0)

        self.v=Scrollbar(self.consolaFrame, orient='vertical')

        self.saliaLb = Text(self.consolaFrame, font=("consolas", 14), yscrollcommand=self.v.set, height=10, background="black", fg="white")
        self.saliaLb.configure(state=DISABLED)

        self.saliaLb.tag_configure("forestgreen", foreground="forest green")
        self.saliaLb.tag_configure("blueviolet", foreground="blue violet")
        self.saliaLb.tag_configure("skyblue", foreground="sky blue")
        self.saliaLb.tag_configure("chocolate", foreground="chocolate")
        self.saliaLb.tag_configure("orange", foreground="orange")
        
        self.saliaLb.grid(sticky="W",row=1,column=0)

        self.v.config(command=self.saliaLb.yview)
        self.v.grid(row=1, column=1,sticky=NS)

        self.consolaFrame.grid(row=3,column=0)

        mainloop()

    def obtenerNombre(self, numNodo):
        dirNodo = self.conf["Direccion Nodo"]["Nodo" + numNodo]
        dirNodo = "http://" + dirNodo + "/nombre"
                
        respuesta = requests.get(dirNodo).text

        return respuesta

    """
    Metodo para poder imprimir el mensaje de los nodos en la consola
    """
    def imprimirConsola(self, texto, color="snow"):
        self.saliaLb.config(state=NORMAL)
        self.saliaLb.insert(END, texto + "\n", color)
        self.saliaLb.config(state=DISABLED)
        self.saliaLb.see(END)

    #Metodos botones

    """
    Metodo que habre una nueva ventana para poder añadir una nueva transacción
    """
    def aniadirTransaccion(self, nombre, numNodos):
        ventanaAniadir = AnidirTrnas(self.window, self.imprimirConsola, nombre,numNodos)

    """
    Metodo para poder controlar el boton de conectado y desconectado
    """
    def controlarBoton(self, numNodo):
        nodo = int(numNodo) - 1
        if not self.estados[nodo]:
            self.conectarNodo(numNodo)
        else:     
            self.desconectarNodo(numNodo)

    """
    Metodo que realiza una peticion para configurar el nodo que se quiere conectar a la red
    """
    def conectarNodo(self, numNodo):
        self.imprimirConsola("Conectado el nodo " + numNodo)

        dirNodo = self.conf["Direccion Nodo"]["Nodo" + numNodo]
        dirNodo = "http://" + dirNodo
        respuesta = ""

        try:
            respuesta = requests.get(dirNodo)
            respuesta.raise_for_status()
            
            respuesta = respuesta.content.decode("utf-8")

            nodo = int(numNodo) - 1
            self.estados[nodo] = not self.estados[nodo]
            self.numNodosConectados = self.numNodosConectados + 1
            self.infoNodosConectado.config(text="Nodos conectados a la red: " + str(self.numNodosConectados))
            self.botones[nodo].config(text="Desconectar")
        except Exception as e:
            respuesta = self.procesarError(e)

        self.imprimirConsola("Nodo " + numNodo + ": " + respuesta, color=self.colores[int(numNodo) - 1])
            
    """
    Metodo que desconecta el nodo de la red
    """
    def desconectarNodo(self, numNodo):
        self.imprimirConsola("Desconentando el nodo " + numNodo)
        dirNodo = self.conf["Direccion Nodo"]["Nodo" + numNodo]
        dirNodo = "http://" + dirNodo

        try:
            respuesta = requests.get(dirNodo+"/desconectar")
            respuesta.raise_for_status()

            respuesta = respuesta.content.decode("utf-8")

            nodo = int(numNodo) - 1
            self.estados[nodo] = not self.estados[nodo]
            self.numNodosConectados = self.numNodosConectados - 1
            self.infoNodosConectado.config(text="Nodos conectados a la red: " + str(self.numNodosConectados))
            self.botones[nodo].config(text="Conectar")
        except Exception  as e:
            respuesta = self.procesarError(e)
               
        self.imprimirConsola("Nodo " + numNodo + ": " + respuesta, color=self.colores[int(numNodo) - 1])
    
    """
    Metodo para procesar los errores de las peticiones de los nodos
    """
    def procesarError (self, e):
        if type(e) == requests.exceptions.HTTPError:
            if e.response.status_code == 401:
                respuesta = e.response.text
        else:
            respuesta = "No se ha encontrado el nodo"

        return respuesta
    
    """
    Metodo para el boton de imprimir la cadena de bloques del nodo selecionador. Esta seleccion se hace atraves de parametros
    """
    def cadenaDeBloques(self, numNodo):
        self.imprimirConsola("Obteniendo bloques del nodo " + numNodo)

        dirNodo = self.conf["Direccion Nodo"]["Nodo" + numNodo]
        dirNodo = "http://" + dirNodo

        try:
            respuesta = requests.get(dirNodo+"/cadena")
            respuesta.raise_for_status()

            respuesta = respuesta.json()["cadena"]
            texto = "Cadena de bloques:\n"

            for bloque in respuesta:
                fCreacion = datetime.fromtimestamp(int(bloque["timestamp"])).strftime("%d/%m/%Y, %H:%M:%S")
                t = "Bloque " + str(bloque["indice"]) + ":\nDatos: " + bloque["datos"] + "\nCreado en: " + fCreacion
                t = t + "\nHash previo: " + bloque["hash_previo"] + "\nNonce: " + str(bloque["nonce"]) + "\nHash: " + bloque["hash"]
                texto = texto + t + "\n"

            respuesta = texto.rstrip('\n')
        except Exception as e:
            respuesta = self.procesarError(e)

        self.imprimirConsola("Nodo " + numNodo + ": " + respuesta, color=self.colores[int(numNodo) - 1])