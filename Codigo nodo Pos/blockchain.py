from hashlib import sha256
import json
import time
import random

from Block import Block

class Blockchain:
    def __init__(self):
        self.transaccionSinConfirmar = []
        self.cadena = []

    def crearBloqueGenesis(self):
        """
        Funcion que crea el bloque genesis, es decir, el primer bloque y lo añade a la cadena
        """
        bloqueGenesis = Block(0, "Bloque Genesis", time.time(), "0")
        bloqueGenesis.hash = bloqueGenesis.calcularHash()
        self.cadena.append(bloqueGenesis)

    @property
    def ultimoBloque(self):
        return self.cadena[-1]

    def nuevoBloque(self, bloque, proof):
        """
        Esta funcion sirve para añadir un nuevo bloque a la red.
        Ademas valida que el hash obtenido en el proceso de mineria sea valido,
        y que el hash del bloque no sea el mismo que el anterior.
        Ademas comprueba que el indice sea superior al ultimo bloque de la red
        """
        bloque.hash = proof
        self.cadena.append(bloque)
        self.borrarPrimeraTransaccion()
        return True

    def validar(self, bloque, proof):
        hash_previo = self.ultimoBloque.hash
        
        if hash_previo != bloque.hash_previo:
            return False
        
        return True

    def proof_of_work(self, bloque):
        """
        Funcion que realiza el minado del bloque, es decir, busca un hash que coincide con los requisitos
        de la red
        """
        bloque.nonce = 0

        hashCalculado = bloque.calcularHash()
        while not hashCalculado.startswith('0' * self.dificultad):
            bloque.nonce += 1
            hashCalculado = bloque.calcularHash()

        return hashCalculado

    def aniadirNuevaTransacción(self, transaction):
        """
        Esta funcion sirve para añadir un bloque. Este bloque se quedara a la espera para que alguien lo mine y lo añada a la red.
        """
        self.transaccionSinConfirmar.append(transaction)
        
    def borrarPrimeraTransaccion(self):
        """
        Esta funcion sirve para añadir un bloque. Este bloque se quedara a la espera para que alguien lo mine y lo añada a la red.
        """
        self.transaccionSinConfirmar.pop()