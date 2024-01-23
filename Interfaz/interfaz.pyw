import configparser
import os
from tkinter import *
from tkinter.ttk import Combobox
from tkinter import messagebox
from interfazInfo import InterfazInfo
from Tooltip import Tooltip

"""Método para poder generar la interfaz de información sobre la red POW"""
def botonPoW ():
    numeroNodos = str(numNodosCB.get())

    try:
        config["Direccion Nodo"]["Nodo"+numeroNodos]
    except Exception as e:
        messagebox.showerror("Error", "Has selecionado más nodos de los que hay configurados")
        return
    
    raiz.destroy()
    raiz.quit()
    interfaz = InterfazInfo(int(numeroNodos), "POW", local)

"""Método para poder generar la interfaz de información sobre la red POS"""
def botonPoS():
    numeroNodos = str(numNodosCB.get())

    try:
        config["Direccion Nodo"]["Nodo"+numeroNodos]
    except Exception as e:
        messagebox.showerror("Error", "Has selecionado más nodos de los que hay configurados")
        return
    
    raiz.destroy()
    raiz.quit()
    interfaz = InterfazInfo(int(numeroNodos), "POS", local)


config = configparser.ConfigParser()
config.read("configuracionInterfaz.ini")
ruta = config["Direccion Nodo"]["Nodo1"]
local=os.path.exists(os.path.dirname(ruta))

raiz = Tk()
raiz.title("Blockchain")
raiz.resizable(False, False)

numNodosFrame = Frame()
numNodosFrame.grid(row=0,column=0, pady=20, padx=20)

numNodosLabel = Label(numNodosFrame,font=("Arial", 16), text="Numero de nodos que deseas: ")
numNodosLabel.grid(row=0, column=0)

valores = ["1", "2", "3", "4", "5"]

numNodosCB = Combobox(numNodosFrame, values=valores, state="readonly")
numNodosCB.current(0)
numNodosCB.grid(row=0, column=1)

tituloFrame = Frame()

tituloFrame.grid(row=1,column=0)

tituloLbl = Label(tituloFrame, text="Selecciona el consenso",font=("Arial", 25),pady=15, padx=15)
tituloLbl.grid(row=0,column=0)

bntFrame = Frame()
bntFrame.grid(row=3,column=0)


bntPOW = Button(bntFrame, text="Consenso POW", command=botonPoW,padx=15)
Tooltip(bntPOW, "Botón para controlar una red con el consenso POW")
bntPOW.grid(row=0,column=0)

bntPOS= Button(bntFrame, text="Consenso POS", command=botonPoS)
Tooltip(bntPOS, "Botón para controlar una red con el consenso POS")
bntPOS.grid(row=0,column=1, padx=20, pady=20)

raiz.mainloop()

