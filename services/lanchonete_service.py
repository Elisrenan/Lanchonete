from domain.cliente import Cliente
from domain.produto import Produto


class LanchoneteService:

    def __init__(self, cliente_repo, produto_repo, pedido_repo):
        self.cliente_repo = cliente_repo
        self.produto_repo = produto_repo
        self.pedido_repo = pedido_repo

    async def criar_cliente(self, cpf: str, nome: str = "") -> Cliente:
        if not cpf.strip():
            raise ValueError("CPF não pode ser vazio")
        existente = await self.cliente_repo.get(cpf)
        if existente:
            return existente
        cliente = Cliente(cpf=cpf, nome=nome)
        await self.cliente_repo.save(cliente)
        return cliente

    async def obter_cliente(self, cpf: str) -> Cliente | None:
        return await self.cliente_repo.get(cpf)

    async def criar_produto(self, codigo: int, valor: float, tipo: int, desconto_percentual: float = 0.0) -> Produto:
        produto = Produto(codigo=codigo, valor=valor, tipo=tipo, desconto_percentual=desconto_percentual)
        await self.produto_repo.save(produto)
        return produto

    async def obter_produto(self, codigo: int) -> Produto | None:
        return await self.produto_repo.get(codigo)

    async def alterar_valor_produto(self, codigo: int, novo_valor: float) -> bool:
        produto = await self.obter_produto(codigo)
        if not produto:
            return False
        produto.valor = float(novo_valor)
        await self.produto_repo.save(produto)
        return True

    async def criar_pedido(self, cpf: str, cod_produto: int, qtd_max_produtos: int) -> dict | None:
        cliente = await self.obter_cliente(cpf)
        produto = await self.obter_produto(cod_produto)
        if not cliente or not produto:
            return None
        codigo = await self.pedido_repo.create(cpf_cliente=cpf, qtd_max_produtos=qtd_max_produtos)
        await self.pedido_repo.add_item(codigo, produto.codigo)
        return await self.pedido_repo.get_raw(codigo)

    async def adicionar_item_pedido(self, cod_pedido: int, cod_produto: int) -> bool:
        raw = await self.pedido_repo.get_raw(cod_pedido)
        if not raw:
            return False
        if raw["esta_cancelado"]:
            return False
        produto = await self.obter_produto(cod_produto)
        if not produto:
            return False
        if len(raw["itens"]) >= int(raw["qtd_max_produtos"]):
            return False
        await self.pedido_repo.add_item(cod_pedido, produto.codigo)
        return True

    async def finalizar_pedido(self, cod_pedido: int) -> float | None:
        raw = await self.pedido_repo.get_raw(cod_pedido)
        if not raw:
            return None
        total = 0.0
        for cod in raw["itens"]:
            p = await self.obter_produto(cod)
            total += p.preco_final()
        await self.pedido_repo.set_entregue(cod_pedido, True)
        return float(total)

    async def obter_pedido_raw(self, cod_pedido: int) -> dict | None:
        return await self.pedido_repo.get_raw(cod_pedido)

    async def cancelar_pedido(self, cod_pedido: int) -> bool:
        raw = await self.pedido_repo.get_raw(cod_pedido)
        if raw is None:
            return False
        if raw["estaEntregue"] or raw["esta_cancelado"]:
            return False
        await self.pedido_repo.set_cancelado(cod_pedido)
        return True

    async def listar_pedidos_cancelados(self) -> list[dict]:
        return await self.pedido_repo.listar_cancelados()

    async def adicionar_observacao(self, cod_pedido: int, observacao: str) -> bool:
        raw = await self.pedido_repo.get_raw(cod_pedido)
        if raw is None:
            return False
        if raw["estaEntregue"]:
            return False
        if observacao is None:
            return False
        observacao = observacao.strip()
        if observacao == "":
            return False
        if len(observacao) > 200:
            return False
        await self.pedido_repo.set_observacao(cod_pedido, observacao)
        return True

    async def buscar_observacao_pedido(self, cod_pedido: int) -> dict | None:
        return await self.pedido_repo.get_raw(cod_pedido)