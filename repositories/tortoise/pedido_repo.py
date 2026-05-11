# =============================================================================
# pedido_repo.py — Repositório de pedidos usando Tortoise ORM
# =============================================================================
#
# Gerencia a persistência de pedidos e seus itens.
# Usa dois modelos: PedidoModel (cabeçalho) e PedidoItemModel (linhas de item).
#
# O método get_raw devolve um dicionário "cru" em vez de um objeto de domínio
# porque o serviço aplica as regras de negócio (desconto, limite) por conta
# própria, consultando os repositórios de produto separadamente.
# =============================================================================

from infrastructure.tortoise.models import PedidoModel, PedidoItemModel


class PedidoRepoTortoise:
    """Repositório assíncrono de pedidos persistidos via Tortoise ORM."""

    async def create(self, cpf_cliente: str, qtd_max_produtos: int) -> int:
        """Cria um novo pedido vazio no banco e retorna seu código gerado.

        O código (PK) é gerado automaticamente pelo SQLite via autoincrement.

        Args:
            cpf_cliente:      CPF do cliente que realizou o pedido.
            qtd_max_produtos: Limite máximo de itens para este pedido.

        Returns:
            Código inteiro gerado pelo banco para o novo pedido.
        """
        pedido = await PedidoModel.create(
            cpf_cliente=cpf_cliente,
            qtd_max_produtos=int(qtd_max_produtos),
            estaEntregue=False,
            esta_cancelado=False,
            observacao="",
        )
        return pedido.codigo

    async def get_raw(self, codigo: int) -> dict | None:
        """Busca um pedido pelo código e retorna um dicionário com todos os dados.

        O dicionário inclui a lista de códigos dos produtos (itens) já adicionados,
        permitindo que o serviço calcule totais e valide limites sem precisar
        de um objeto de domínio Pedido.

        Args:
            codigo: Código do pedido a buscar.

        Returns:
            Dict com chaves: codigo, cpf_cliente, qtd_max_produtos, estaEntregue,
            esta_cancelado, observacao, itens (lista de códigos de produtos).
            Retorna None se o pedido não existir.
        """
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
        """Adiciona um produto (item) a um pedido existente.

        Cada chamada insere uma linha em PedidoItemModel.
        Não valida limite aqui: a validação é responsabilidade do serviço.

        Args:
            pedido_codigo:  Código do pedido que receberá o item.
            produto_codigo: Código do produto a adicionar.
        """
        await PedidoItemModel.create(
            pedido_codigo=int(pedido_codigo),
            produto_codigo=int(produto_codigo),
        )

    async def set_entregue(self, pedido_codigo: int, entregue: bool) -> None:
        """Marca o pedido como entregue (ou reverte, se entregue=False).

        Args:
            pedido_codigo: Código do pedido a atualizar.
            entregue:      Novo estado do campo estaEntregue.
        """
        await PedidoModel.filter(codigo=int(pedido_codigo)).update(estaEntregue=bool(entregue))

    async def set_cancelado(self, pedido_codigo: int) -> None:
        """Marca o pedido como cancelado.

        Args:
            pedido_codigo: Código do pedido a cancelar.
        """
        await PedidoModel.filter(codigo=int(pedido_codigo)).update(esta_cancelado=True)

    async def set_observacao(self, pedido_codigo: int, observacao: str) -> None:
        """Grava ou substitui a observação de um pedido.

        Args:
            pedido_codigo: Código do pedido a atualizar.
            observacao:    Texto da observação (já validado pelo serviço).
        """
        await PedidoModel.filter(codigo=int(pedido_codigo)).update(observacao=observacao)

    async def listar_cancelados(self) -> list[dict]:
        """Retorna todos os pedidos com esta_cancelado=True.

        Para cada pedido, carrega também seus itens (produto_codigo).

        Returns:
            Lista de dicionários no mesmo formato de get_raw.
        """
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
