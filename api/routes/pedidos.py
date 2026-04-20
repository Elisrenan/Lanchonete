from fastapi import APIRouter, HTTPException
from schemas.pedido import PedidoCreate, PedidoAddItem, PedidoOut
from services.lanchonete_service import service

router = APIRouter(prefix="/lanchonete/pedidos", tags=["pedidos"])
@router.post("", response_model=PedidoOut)
def criar(payload: PedidoCreate):
    pedido = service.criar_pedido(payload.cpf, payload.cod_produto, payload.qtd_max_produtos)
    if not pedido:
        raise HTTPException(status_code=400, detail="CPF ou produto inválido")
    return PedidoOut(
        codigo=pedido.codigo,
        cpf=pedido.cliente.cpf,
        esta_entregue=pedido.esta_entregue,
        produtos=[p.codigo for p in pedido.listaProdutos],
    )

@router.put("/{cod_pedido}/itens")
def adicionar_item(cod_pedido: int, payload: PedidoAddItem):
    ok = service.alterar_pedido(cod_pedido, payload.cod_produto)
    if not ok:
        raise HTTPException(status_code=400, detail="Pedido/produto inválido ou limite excedido")
    return {"ok": True}

@router.post("/{cod_pedido}/finalizar")
def finalizar(cod_pedido: int):
    total = service.finalizar_pedido(cod_pedido)
    if total is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return {"total": total}

@router.get("/{cod_pedido}", response_model=PedidoOut)
def obter(cod_pedido: int):
    pedido = service.obter_pedido(cod_pedido)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return PedidoOut(
        codigo=pedido.codigo,
        cpf=pedido.cliente.cpf,
        esta_entregue=pedido.esta_entregue,
        produtos=[p.codigo for p in pedido.listaProdutos],
    )