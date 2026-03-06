from pydantic import BaseModel

class ProdutoCreate(BaseModel):
    id: int
    tipo: int
    valor: float
    desconto_percentual: float = 0.0

class ProdutoOut(BaseModel):
    id: int
    tipo: int
    valor: float
    desconto_percentual: float = 0.0

