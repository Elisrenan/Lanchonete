from fastapi import APIRouter, HTTPException, Depends
from schemas.cliente import ClienteCreate, ClienteOut
from services.lanchonete_service import LanchoneteService
from app.deps import get_service_tortoise

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("", response_model=ClienteOut)
async def criar(payload: ClienteCreate, svc: LanchoneteService = Depends(get_service_tortoise)):
    """Cria um novo cliente ou retorna o existente com o mesmo CPF."""
    try:
        cliente = await svc.criar_cliente(payload.cpf, payload.nome)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ClienteOut(cpf=cliente.cpf, nome=cliente.nome)


@router.get("/{cpf}", response_model=ClienteOut)
async def obter(cpf: str, svc: LanchoneteService = Depends(get_service_tortoise)):
    """Busca um cliente pelo CPF."""
    cliente = await svc.obter_cliente(cpf)
    if not cliente:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
            )
    return ClienteOut(cpf=cliente.cpf, nome=cliente.nome)