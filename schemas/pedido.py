from pydantic import BaseModel
from typing import List


class PedidoCreate(BaseModel):
    """Payload para criação de um pedido."""

    cpf: str
    cod_produto: int
    qtd_max_produtos: int = 10


class PedidoAddItem(BaseModel):
    """Payload para adicionar um item a um pedido existente."""

    cod_produto: int


class PedidoOut(BaseModel):
    """Dados de retorno de um pedido."""

    codigo: int
    cpf: str
    esta_entregue: bool
    esta_cancelado: bool
    produtos: List[int]