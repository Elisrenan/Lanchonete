from fastapi import APIRouter, HTTPException
from schemas.pedido import PedidoCreate, PedidoAddItem, PedidoOut
from services.lanchonete_service import service

router = APIRouter(prefix="/lanchonete/pedidos", tags=["pedidos"])


@router.post("", response_model=PedidoOut)
def criar(payload: PedidoCreate):
    """Cria um pedido com o primeiro produto já adicionado."""
    pedido = service.criar_pedido(payload.cpf, payload.cod_produto, payload.qtd_max_produtos)
    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Cliente ou produto não encontrado"
        )

    return PedidoOut(
        codigo=pedido.codigo,
        cpf=pedido.cliente.cpf,
        esta_entregue=pedido.esta_entregue,
        esta_cancelado=pedido.esta_cancelado,
        produtos=[p.codigo for p in pedido.listaProdutos],
    )


@router.put("/{cod_pedido}/itens")
def adicionar_item(cod_pedido: int, payload: PedidoAddItem):
    """Adiciona um produto a um pedido existente."""
    ok = service.alterar_pedido(cod_pedido, payload.cod_produto)
    if not ok:
        raise HTTPException(
            status_code=400,
            detail="Pedido/produto inválido ou limite excedido"
        )
    return {"ok": True}


@router.post("/{cod_pedido}/finalizar")
def finalizar(cod_pedido: int):
    """Finaliza um pedido e retorna o total calculado."""
    total = service.finalizar_pedido(cod_pedido)
    if total is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return {"total": total}


@router.get("/cancelados", response_model=list[PedidoOut])
def listar_pedidos_cancelados():
    """Lista todos os pedidos cancelados."""
    pedidos = service.listar_pedidos_cancelados()
    return [
        PedidoOut(
            codigo=p.codigo,
            cpf=p.cliente.cpf,
            esta_entregue=p.esta_entregue,
            esta_cancelado=p.esta_cancelado,
            produtos=[prod.codigo for prod in p.listaProdutos],
        )
        for p in pedidos
    ]


@router.get("/{cod_pedido}", response_model=PedidoOut)
def obter(cod_pedido: int):
    """Busca um pedido pelo código."""
    pedido = service.obter_pedido(cod_pedido)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return PedidoOut(
        codigo=pedido.codigo,
        cpf=pedido.cliente.cpf,
        esta_entregue=pedido.esta_entregue,
        esta_cancelado=pedido.esta_cancelado,
        produtos=[p.codigo for p in pedido.listaProdutos],
    )


@router.patch("/{cod_pedido}/cancelar")
def cancelar_pedido(cod_pedido: int):
    """Cancela um pedido existente."""
    resultado = service.cancelar_pedido(cod_pedido)
    if not resultado:
        raise HTTPException(
            status_code=400,
            detail="Pedido não encontrado ou não pode ser cancelado",
        )
    return {"ok": True, "mensagem": "Pedido cancelado com sucesso"}