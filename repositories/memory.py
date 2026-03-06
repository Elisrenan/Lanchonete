from typing import Dict
from domain.cliente import Cliente
from domain.produto import Produto

class MemoryDB:
    def __init__(self):
        self.clientes_por_cpf: Dict[str, Cliente] = {}
        self.produtos_por_id: Dict[int, Produto] = {}

db = MemoryDB()