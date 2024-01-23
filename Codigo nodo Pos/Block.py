from hashlib import sha256
import json
import time
import random

class Block:
    def __init__(self, indice, datos, timestamp, hash_previo):
        self.indice = indice
        self.datos = datos
        self.timestamp = timestamp
        self.hash_previo = hash_previo
        self.nonce = 0

    def calcularHash(self):
        """
        Funcion que devuelve el hash del bloque
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()
        