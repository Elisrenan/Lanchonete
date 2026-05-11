from fastapi import APIRouter, HTTPException, Depends
from schemas.produto import ProdutoCreate, ProdutoOut, ProdutoAlterarValor
from services.lanchonete_service import LanchoneteService
from app.deps import get_service_tortoise

router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.post("", response_model=ProdutoOut)
async def criar(payload: ProdutoCreate, svc: LanchoneteService = Depends(get_service_tortoise)):
    """Cria um novo produto."""
    produto = await svc.criar_produto(
        payload.codigo,
        payload.valor,
        payload.tipo,
        payload.desconto_percentual
    )
    return ProdutoOut(**produto.__dict__)


@router.get("/{codigo}", response_model=ProdutoOut)
async def obter(codigo: int, svc: LanchoneteService = Depends(get_service_tortoise)):
    """Busca um produto pelo código."""
    produto = await svc.obter_produto(codigo)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return ProdutoOut(**produto.__dict__)


@router.put("/{codigo}/valor")
async def alterar_valor(codigo: int, payload: ProdutoAlterarValor, svc: LanchoneteService = Depends(get_service_tortoise)):
    """Atualiza o valor de um produto existente."""
    alterou = await svc.alterar_valor_produto(codigo, payload.novo_valor)
    if not alterou:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {"alterou": True}
