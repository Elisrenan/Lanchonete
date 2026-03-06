from fastapi import APIRouter, HTTPException
from schemas.produto import ProdutoCreate, ProdutoOut
from services.lanchonete_service import service

router = APIRouter(prefix="/produtos", tags=["produtos"])

@router.post("", response_model=ProdutoOut)
def criar(payload: ProdutoCreate):
    produto = service.criar_produto(payload.id, payload.tipo, payload.valor, payload.desconto_percentual)
    return ProdutoOut(id=produto.id, tipo=produto.tipo, valor=produto.valor, desconto_percentual=produto.desconto_percentual)