import os
from subprocess import Popen
import sys
import threading
from tkinter import *
import webbrowser
from interfazPOW import InterfazPow
from interfazPOS import InterfazPos
import configparser
import shutil
from Tooltip import Tooltip

class InterfazInfo:
    """Contructor del objeto. Inicializa las variables necesarias"""
    def __init__(self, numNodos, consenso, local):
        self.numNodos = numNodos
        self.local = local
        self.cargarVentana(consenso)
    
    """Método para poder cargar los elementodos de la interfaz"""
    def cargarVentana(self, consenso):
        self.ventana = Tk()
        self.ventana.title("Información")

        superiorFrame = Frame()
        superiorFrame.grid(row=0,column=0, padx=20, pady=20)

        tituloFrame = Label(superiorFrame, text="Información sobre la red", font=("Arial", 20))
        tituloFrame.grid(row=0, column=0)

        textoFrame = Frame()
        textoFrame.grid(row=1, column=0, padx=20)
 
        aniadidosLabel = Label(textoFrame, text="Se van a añadir " + str(self.numNodos) + " nodos a la red", font=("Arial", 14))
        aniadidosLabel.grid(row=0, column=0)

        if(self.local):
            inforAbrirLabel = Label(textoFrame, text="Al dar al boton Continuar, se van a a abrir " + str(self.numNodos + 1) + " ventanas.", font=("Arial", 14))
            inforAbrirLabel.grid(row=1, column=0)

            inforAbrirLabel2 = Label(textoFrame, text="Una por cada nodo y el controlador de la red. Estas son las cosolas de dichos nodos", font=("Arial", 14))
            inforAbrirLabel2.grid(row=2, column=0)

        consesoLabel = Label(textoFrame, text="Has selecionado el consenso: " + consenso, font=("Arial", 14))
        consesoLabel.grid(row=3,column=0)

        enlace = "https://es.wikipedia.org/wiki/Prueba_de_apuesta" if consenso == "POS" else "https://es.wikipedia.org/wiki/Sistema_de_prueba_de_trabajo"

        masInfoLabel = Label(textoFrame, text="Para más informacion, acude al siguiente enlacen:", font=("Arial", 14))
        masInfoLabel.grid(row=4,column=0)

        enlaceLabel = Label(textoFrame, text=enlace, font=("Arial", 14), cursor='hand2', fg="blue")
        enlaceLabel.grid(row=5,column=0)

        enlaceLabel.bind('<Button-1>', lambda e: webbrowser.open(enlace))


        botonFrame = Frame()
        botonFrame.grid(row=2, column=0, pady=20)

        continuarBt = Button(botonFrame, text="Continuar", command=lambda: self.continuar(consenso))
        Tooltip(continuarBt, "Botón pasar a la interfaz para controlar la red")
        continuarBt.grid(row=0,column=0)
        
        mainloop()

    """Método del boton continuar, este inicializa los nodos, abrir la ventana de control y abrir la ventana de control e la red"""
    def continuar(self, consenso):
        if (self.local):
            self.iniciarNodos()
        else: #El fichero de configuracion tiene direcciones ip, se procede a copiarlo
            shutil.copyfile("configuracionInterfaz.ini", "dirNodos.ini")

        if (consenso == "POW"):
            self.ventana.quit()
            self.ventana.destroy()
            interfaz = InterfazPow(int(self.numNodos))
        else:
            self.ventana.quit()
            self.ventana.destroy()
            interfaz = InterfazPos(int(self.numNodos))

    """Método que se encarga de ejecutar el proceso el nodo o controlador"""
    def lanzarNodo(self, ruta, archivo):
        os.chdir(ruta)
        Popen(["python", archivo])      

    """Método para poder ejecutar todos los nodos seleccionados"""
    def iniciarNodos(self):
        rutaInterfaz = os.getcwd()

        config = configparser.ConfigParser()
        config.read("configuracionInterfaz.ini")

        config2 = configparser.ConfigParser()
        config2.add_section("Direccion Nodo")

        for i in range(1,self.numNodos + 1):
            ruta = config["Direccion Nodo"]["Nodo"+str(i)]
            ip = self.obtenerIpNodo(ruta)
            config2.set("Direccion Nodo", "Nodo"+str(i),ip)
            self.lanzarNodo(ruta,"nodoApi.py")

        ruta = config["Direccion Nodo"]["Nodo1"]
        self.lanzarNodo(ruta,"controlador.py")

        os.chdir(rutaInterfaz)

        with open("dirNodos.ini", 'w') as archivo:
            config2.write(archivo)

    """Método para obtener la ip del nodo que se desea ejecutrar. Esta ip se obtiene de su archivo de configuración"""
    def obtenerIpNodo(self, ruta):
        os.chdir(ruta)
        config = configparser.ConfigParser()
        config.read("configuracionNodo.ini")
        return config["Nodo"]["tarjetaRed"] + ":" + config["Nodo"]["puerto"] 