from infrastructure.tortoise.models import PedidoModel, PedidoItemModel


class PedidoRepoTortoise:
    async def create(self, cpf_cliente: str, qtd_max_produtos: int) -> int:
        pedido = await PedidoModel.create(
            cpf_cliente=cpf_cliente,
            qtd_max_produtos=int(qtd_max_produtos),
            estaEntregue=False,
            esta_cancelado=False,
            observacao="",
        )
        return pedido.codigo

    async def get_raw(self, codigo: int) -> dict | None:
        pedido = await PedidoModel.get_or_none(codigo=int(codigo))
        if not pedido:
            return None
        itens = await PedidoItemModel.filter(pedido_codigo=pedido.codigo).all()
        return {
            "codigo": pedido.codigo,
            "cpf_cliente": pedido.cpf_cliente,
            "qtd_max_produtos": pedido.qtd_max_produtos,
            "estaEntregue": pedido.estaEntregue,
            "esta_cancelado": pedido.esta_cancelado,
            "observacao": pedido.observacao,
            "itens": [i.produto_codigo for i in itens],
        }

    async def add_item(self, pedido_codigo: int, produto_codigo: int) -> None:
        await PedidoItemModel.create(
            pedido_codigo=int(pedido_codigo),
            produto_codigo=int(produto_codigo),
        )

    async def set_entregue(self, pedido_codigo: int, entregue: bool) -> None:
        await PedidoModel.filter(codigo=int(pedido_codigo)).update(estaEntregue=bool(entregue))

    async def set_cancelado(self, pedido_codigo: int) -> None:
        await PedidoModel.filter(codigo=int(pedido_codigo)).update(esta_cancelado=True)

    async def set_observacao(self, pedido_codigo: int, observacao: str) -> None:
        await PedidoModel.filter(codigo=int(pedido_codigo)).update(observacao=observacao)

    async def listar_cancelados(self) -> list[dict]:
        pedidos = await PedidoModel.filter(esta_cancelado=True).all()
        result = []
        for pedido in pedidos:
            itens = await PedidoItemModel.filter(pedido_codigo=pedido.codigo).all()
            result.append({
                "codigo": pedido.codigo,
                "cpf_cliente": pedido.cpf_cliente,
                "qtd_max_produtos": pedido.qtd_max_produtos,
                "estaEntregue": pedido.estaEntregue,
                "esta_cancelado": pedido.esta_cancelado,
                "observacao": pedido.observacao,
                "itens": [i.produto_codigo for i in itens],
            })
        return result
