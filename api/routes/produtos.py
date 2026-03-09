from fastapi import APIRouter, HTTPException
from schemas.produto import ProdutoCreate, ProdutoOut, ProdutoAlterarValor
from services.lanchonete_service import service

router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.post("", response_model=ProdutoOut)
def criar(payload: ProdutoCreate):
    produto = service.criar_produto(
        payload.codigo,
        payload.valor,
        payload.tipo,
        payload.desconto_percentual
    )
    return ProdutoOut(**produto.__dict__)


@router.get("/{codigo}", response_model=ProdutoOut)
def obter(codigo: int):
    produto = service.obter_produto(codigo)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return ProdutoOut(**produto.__dict__)


@router.put("/{codigo}/valor")
def alterar_valor(codigo: int, payload: ProdutoAlterarValor):
    alterou = service.alterar_valor_produto(codigo, payload.novo_valor)
    if not alterou:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {"alterou": True}
