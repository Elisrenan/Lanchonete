from fastapi import APIRouter, HTTPException, Depends
from schemas.pedido import PedidoCreate, PedidoAddItem, PedidoOut, ObservacaoInput, ObservacaoOut
from services.lanchonete_service import LanchoneteService
from app.deps import get_service_tortoise

router = APIRouter(prefix="/lanchonete/pedidos", tags=["pedidos"])


def _raw_to_pedido_out(raw: dict) -> PedidoOut:
    return PedidoOut(
        codigo=raw["codigo"],
        cpf=raw["cpf_cliente"],
        esta_entregue=raw["estaEntregue"],
        esta_cancelado=raw["esta_cancelado"],
        produtos=raw["itens"],
    )


@router.post("", response_model=PedidoOut)
async def criar(payload: PedidoCreate, svc: LanchoneteService = Depends(get_service_tortoise)):
    """Cria um pedido com o primeiro produto já adicionado."""
    raw = await svc.criar_pedido(payload.cpf, payload.cod_produto, payload.qtd_max_produtos)
    if not raw:
        raise HTTPException(
            status_code=404,
            detail="Cliente ou produto não encontrado"
        )
    return _raw_to_pedido_out(raw)


@router.put("/{cod_pedido}/itens")
async def adicionar_item(cod_pedido: int, payload: PedidoAddItem, svc: LanchoneteService = Depends(get_service_tortoise)):
    """Adiciona um produto a um pedido existente."""
    ok = await svc.adicionar_item_pedido(cod_pedido, payload.cod_produto)
    if not ok:
        raise HTTPException(
            status_code=400,
            detail="Pedido/produto inválido ou limite excedido"
        )
    return {"ok": True}


@router.post("/{cod_pedido}/finalizar")
async def finalizar(cod_pedido: int, svc: LanchoneteService = Depends(get_service_tortoise)):
    """Finaliza um pedido e retorna o total calculado."""
    total = await svc.finalizar_pedido(cod_pedido)
    if total is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return {"total": total}


@router.get("/{cod_pedido}/observacao", response_model=ObservacaoOut)
async def buscar_observacao(cod_pedido: int, svc: LanchoneteService = Depends(get_service_tortoise)):
    """Retorna a observação registrada em um pedido."""
    raw = await svc.buscar_observacao_pedido(cod_pedido)
    if not raw:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return ObservacaoOut(codigo=raw["codigo"], observacao=raw["observacao"])


@router.get("/cancelados", response_model=list[PedidoOut])
async def listar_pedidos_cancelados(svc: LanchoneteService = Depends(get_service_tortoise)):
    """Lista todos os pedidos cancelados."""
    cancelados = await svc.listar_pedidos_cancelados()
    return [_raw_to_pedido_out(raw) for raw in cancelados]


@router.get("/{cod_pedido}", response_model=PedidoOut)
async def obter(cod_pedido: int, svc: LanchoneteService = Depends(get_service_tortoise)):
    """Busca um pedido pelo código."""
    raw = await svc.obter_pedido_raw(cod_pedido)
    if not raw:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return _raw_to_pedido_out(raw)


@router.patch("/{cod_pedido}/cancelar")
async def cancelar_pedido(cod_pedido: int, svc: LanchoneteService = Depends(get_service_tortoise)):
    """Cancela um pedido existente."""
    resultado = await svc.cancelar_pedido(cod_pedido)
    if not resultado:
        raise HTTPException(
            status_code=400,
            detail="Pedido não encontrado ou não pode ser cancelado",
        )
    return {"ok": True, "mensagem": "Pedido cancelado com sucesso"}


@router.post("/{cod_pedido}/observacao")
async def adicionar_observacao(cod_pedido: int, body: ObservacaoInput, svc: LanchoneteService = Depends(get_service_tortoise)):
    """Adiciona ou substitui a observação de um pedido."""
    resultado = await svc.adicionar_observacao(cod_pedido, body.observacao)
    if not resultado:
        raise HTTPException(
            status_code=400,
            detail="Pedido não encontrado ou inválido",
        )
    return {"ok": True, "mensagem": "Observação adicionada com sucesso"}


@router.get("/{cod_pedido}/observacao", response_model=ObservacaoOut)
def buscar_observacao(cod_pedido: int):
    """Retorna a observação de um pedido."""
    pedido = service.buscar_observacao_pedido(cod_pedido)
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return ObservacaoOut(
        codigo=pedido.codigo,
        observacao=pedido.observacao,
    )