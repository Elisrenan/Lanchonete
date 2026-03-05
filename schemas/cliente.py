from pydantic import BaseModel

class ClienteCreate(BaseModel):
    cpf: str
    nome: str = ""

class ClienteOut(BaseModel):
    cpf: str
    nome: str = ""

