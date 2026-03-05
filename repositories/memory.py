from typing import Dict
from domain.cliente import Cliente

class MemoryDB:
    def __init__(self):
        self.clientes_por_cpf: Dict[str, Cliente] = {}

db = MemoryDB()