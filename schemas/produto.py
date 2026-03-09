from pydantic import BaseModel

class ProdutoCreate(BaseModel):
    codigo: int
    valor: float
    tipo: int
    desconto_percentual: float = 0.0

class ProdutoOut(BaseModel):
    codigo: int
    valor: float
    tipo: int
    desconto_percentual: float = 0.0

class ProdutoAlterarValor(BaseModel):
    novo_valor: float
