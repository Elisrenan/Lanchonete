from fastapi import APIRouter, HTTPException
from schemas.cliente import ClienteCreate, ClienteOut
from services.lanchonete_service import service

router = APIRouter(prefix="/clientes", tags=["clientes"])

@router.post("", response_model=ClienteOut)
def criar(payload: ClienteCreate):
    cliente = service.criar_cliente(payload.cpf, payload.nome)
    return ClienteOut(cpf=cliente.cpf, nome=cliente.nome)

@router.get("/{cpf}", response_model=ClienteOut)
def obter(cpf: str):
    cliente = service.obter_cliente(cpf)
    if not cliente:
        raise HTTPException(
            status_code=404, 
            detail="Cliente não encontrado"
            )
    return ClienteOut(cpf=cliente.cpf, nome=cliente.nome)