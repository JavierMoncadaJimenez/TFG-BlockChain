import tkinter as tk
from tkinter import *
from configparser import ConfigParser
import requests

class AnidirTrnas():
    def __init__(self, padre, actualizar, nombre, numNodos):
        self.conf = ConfigParser()
        self.conf.read("dirNodos.ini")
        self.nodos = []
        self.autor = ""
        self.contenido = ""
        self.nombre = nombre
        self.numNodos = numNodos
        self.cargarNodos()
        self.cargarVentana(padre, actualizar)
        

    def cargarNodos(self):
        for i in range (1,self.numNodos + 1):
            self.nodos.append(self.conf["Direccion Nodo"]["Nodo" + str(i)]) 

    def cargarVentana(self, padre, actualizar):
        self.window= Toplevel(padre) 
        self.window.title('Añadar Transaccion')

        #Frame para los textArea
        self.frameSuperior = Frame(self.window)
        self.frameSuperior.grid(row=0,column=0,padx=10)

        self.autorLb = Label(self.frameSuperior, text="Autor",font=("Arial", 14))
        self.autorLb.grid(row=0,column=0, sticky="W")

        self.contenidoLb = Label(self.frameSuperior, text="Contenido",font=("Arial", 14))
        self.contenidoLb.grid(row=0,column=1,padx=(100), sticky="W")

        self.autorTxB = Text(self.frameSuperior, height=1, width=20)
        self.autorTxB.insert(END, self.nombre)
        self.autorTxB.config(state=DISABLED)
        self.autorTxB.grid(row=1, column=0, pady=10)

        self.contenidoTxB = Text(self.frameSuperior, height=2,width=40)
        self.contenidoTxB.grid(row=1, column=1, pady=10,padx=(100,10))

        #Frame para los Botones
        self.frameInferior = Frame(self.window)
        self.frameInferior.grid(row=1,column=0)

        self.aniadirBt = Button(self.frameInferior, text="Añadir", command=lambda: self.aniadir(actualizar))
        self.aniadirBt.grid(row=0, column=0)

        self.cancelarBt = Button(self.frameInferior,text="Cancelar", command=self.cancelar)
        self.cancelarBt.grid(row=0,column=1, padx=(10,0))

        mainloop()


    def cancelar(self):
        self.window.destroy()

    def aniadir(self, actualizar):
        texto = ""
        for dirNodo in self.nodos:
            try:
                self.autor = self.autorTxB.get("1.0",'end-1c')
                self.contenido = self.contenidoTxB.get("1.0",'end-1c')
                data = {"autor": self.autor, "contenido": self.contenido}
                requests.post("http://" + dirNodo + "/nueva_transaccion",json=data)
                texto = "\nTransacción añadida:\nAutor: " + self.autor + "\nContenido: " + self.contenido
                break
            except requests.exceptions.RequestException as e:
                texto="\nNo se ha añadido la transacción, no hay nodos en la red"
                continue
        actualizar(texto)
        self.window.destroy()

