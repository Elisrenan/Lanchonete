# =============================================================================
# lanchonete_service.py — Camada de serviço (regras de negócio)
# =============================================================================
#
# O serviço coordena as operações da aplicação. Ele:
#   - Recebe parâmetros simples (cpf, codigo, etc.) das rotas
#   - Aplica regras de negócio (validações, limites, cálculos)
#   - Delega a persistência aos repositórios (cliente_repo, produto_repo, pedido_repo)
#   - Devolve entidades de domínio (Cliente, Produto) ou dicionários raw (pedidos)
#
# Com Tortoise ORM, todos os métodos que acessam o banco são async.
# As rotas usam `await` para chamarem o serviço.
# =============================================================================

from domain.cliente import Cliente
from domain.produto import Produto


class LanchoneteService:
    """Serviço principal com as regras de negócio da lanchonete.

    Recebe os repositórios por injeção de dependência, mantendo
    o código desacoplado da implementação de persistência.
    """
    def __init__(self, cliente_repo, produto_repo, pedido_repo):
        """Inicializa o serviço injetando os três repositórios.

        Args:
            cliente_repo: Repositório de clientes (ClienteRepoTortoise ou qualquer impl.).
            produto_repo: Repositório de produtos.
            pedido_repo:  Repositório de pedidos e seus itens.
        """
        self.cliente_repo = cliente_repo
        self.produto_repo = produto_repo
        self.pedido_repo = pedido_repo

    async def criar_cliente(self, cpf: str, nome: str = "") -> Cliente:
        """Cria um novo cliente ou retorna o existente com o mesmo CPF.

        Args:
            cpf:  CPF do cliente (não pode ser vazio ou apenas espaços).
            nome: Nome do cliente (opcional).

        Returns:
            Cliente criado ou já existente.

        Raises:
            ValueError: Se o CPF for vazio.
        """
        if not cpf.strip():
            raise ValueError("CPF não pode ser vazio")
        existente = await self.cliente_repo.get(cpf)
        if existente:
            return existente
        cliente = Cliente(cpf=cpf, nome=nome)
        await self.cliente_repo.save(cliente)
        return cliente

    async def obter_cliente(self, cpf: str) -> Cliente | None:
        """Busca um cliente pelo CPF.

        Returns:
            Cliente encontrado ou None.
        """
        return await self.cliente_repo.get(cpf)

    async def criar_produto(self, codigo: int, valor: float, tipo: int, desconto_percentual: float = 0.0) -> Produto:
        """Cria e persiste um novo produto.

        Args:
            codigo:               Identificador único do produto.
            valor:                Preço base (deve ser >= 0).
            tipo:                 1 = com desconto | 2 = sem desconto.
            desconto_percentual:  Percentual de desconto. Padrão: 0.

        Returns:
            Produto criado e persistido.
        """
        produto = Produto(codigo=codigo, valor=valor, tipo=tipo, desconto_percentual=desconto_percentual)
        await self.produto_repo.save(produto)
        return produto

    async def obter_produto(self, codigo: int) -> Produto | None:
        """Busca um produto pelo código.

        Returns:
            Produto encontrado ou None.
        """
        return await self.produto_repo.get(codigo)

    async def alterar_valor_produto(self, codigo: int, novo_valor: float) -> bool:
        """Atualiza o preço base de um produto existente.

        Args:
            codigo:     Código do produto.
            novo_valor: Novo valor a ser atribuído.

        Returns:
            True se alterado, False se o produto não foi encontrado.
        """
        produto = await self.obter_produto(codigo)
        if not produto:
            return False
        produto.valor = float(novo_valor)
        await self.produto_repo.save(produto)
        return True

    async def criar_pedido(self, cpf: str, cod_produto: int, qtd_max_produtos: int) -> dict | None:
        """Cria um pedido com o primeiro produto já adicionado.

        O código do pedido é gerado pelo banco (autoincrement).

        Args:
            cpf:              CPF do cliente.
            cod_produto:      Código do primeiro produto do pedido.
            qtd_max_produtos: Limite máximo de produtos no pedido.

        Returns:
            Dicionário raw do pedido criado, ou None se cliente/produto não encontrado.
        """
        cliente = await self.obter_cliente(cpf)
        produto = await self.obter_produto(cod_produto)
        if not cliente or not produto:
            return None
        codigo = await self.pedido_repo.create(cpf_cliente=cpf, qtd_max_produtos=qtd_max_produtos)
        await self.pedido_repo.add_item(codigo, produto.codigo)
        return await self.pedido_repo.get_raw(codigo)

    async def adicionar_item_pedido(self, cod_pedido: int, cod_produto: int) -> bool:
        """Adiciona um produto a um pedido existente.

        Valida: pedido existe, não está cancelado, produto existe e limite não foi atingido.

        Args:
            cod_pedido:  Código do pedido.
            cod_produto: Código do produto a adicionar.

        Returns:
            True se adicionado, False se qualquer validação falhar.
        """
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
        """Finaliza um pedido, calcula o total e marca como entregue.

        O total é a soma de preco_final() de cada produto (regra do domínio).

        Args:
            cod_pedido: Código do pedido.

        Returns:
            Total calculado como float, ou None se o pedido não existir.
        """
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
        """Busca um pedido pelo código e retorna dicionário raw.

        Returns:
            Dict com todos os dados do pedido, ou None se não encontrado.
        """
        return await self.pedido_repo.get_raw(cod_pedido)

    async def cancelar_pedido(self, cod_pedido: int) -> bool:
        """Cancela um pedido existente, desde que não esteja finalizado ou já cancelado.

        Args:
            cod_pedido: Código do pedido.

        Returns:
            True se cancelado com sucesso, False caso contrário.
        """
        raw = await self.pedido_repo.get_raw(cod_pedido)
        if raw is None:
            return False
        if raw["estaEntregue"] or raw["esta_cancelado"]:
            return False
        await self.pedido_repo.set_cancelado(cod_pedido)
        return True

    async def listar_pedidos_cancelados(self) -> list[dict]:
        """Retorna todos os pedidos com esta_cancelado=True.

        Returns:
            Lista de dicionários raw de pedidos cancelados.
        """
        return await self.pedido_repo.listar_cancelados()

    async def adicionar_observacao(self, cod_pedido: int, observacao: str) -> bool:
        """Adiciona ou substitui a observação de um pedido.

        Regras:
            - Pedido deve existir.
            - Pedido não pode estar finalizado (estaEntregue).
            - Observação não pode ser vazia ou apenas espaços.
            - Observação não pode ultrapassar 200 caracteres.

        Args:
            cod_pedido:  Código do pedido.
            observacao:  Texto da observação.

        Returns:
            True se registrada, False se alguma regra for violada.
        """
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
        """Busca os dados de um pedido para consulta da observação.

        Returns:
            Dict raw do pedido ou None se não encontrado.
        """
        return await self.pedido_repo.get_raw(cod_pedido)