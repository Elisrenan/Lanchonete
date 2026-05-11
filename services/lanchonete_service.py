from domain.cliente import Cliente
from domain.pedido import Pedido
from domain.produto import Produto
from repositories.memory import db


class LanchoneteService:
    """Serviço principal com as regras de negócio da lanchonete.

    Coordena operações sobre clientes, produtos e pedidos,
    delegando a persistência ao repositório em memória.
    """

    def criar_cliente(self, cpf: str, nome: str = "") -> Cliente:
        """Cria um novo cliente ou retorna o existente com o mesmo CPF.

        Args:
            cpf: CPF do cliente (não pode ser vazio ou apenas espaços).
            nome: Nome do cliente (opcional).

        Returns:
            Cliente criado ou já existente.

        Raises:
            ValueError: Se o CPF for vazio.
        """
        if not cpf.strip():
            raise ValueError("CPF não pode ser vazio")

        if cpf in db.clientes_por_cpf:
            return db.clientes_por_cpf[cpf]
        cliente = Cliente(cpf=cpf, nome=nome)
        db.clientes_por_cpf[cpf] = cliente
        return cliente

    def obter_cliente(self, cpf: str) -> Cliente | None:
        """Busca um cliente pelo CPF.

        Returns:
            Cliente encontrado ou None.
        """
        return db.clientes_por_cpf.get(cpf)

    def criar_produto(self, codigo: int, valor: float, tipo: int, desconto_percentual: float = 0.0) -> Produto:
        """Cria e persiste um novo produto.

        Args:
            codigo: Identificador único do produto.
            valor: Preço base.
            tipo: Tipo do produto (1 = com desconto, 2 = sem desconto).
            desconto_percentual: Percentual de desconto a aplicar. Padrão: 0.

        Returns:
            Produto criado.
        """
        produto = Produto(codigo=codigo, valor=valor, tipo=tipo, desconto_percentual=desconto_percentual)
        db.produtos_por_id[codigo] = produto
        return produto

    def obter_produto(self, codigo: int) -> Produto | None:
        """Busca um produto pelo código.

        Returns:
            Produto encontrado ou None.
        """
        return db.produtos_por_id.get(codigo)

    def alterar_valor_produto(self, codigo: int, novo_valor: float) -> bool:
        """Atualiza o preço base de um produto existente.

        Args:
            codigo: Código do produto.
            novo_valor: Novo valor a ser atribuído.

        Returns:
            True se alterado, False se o produto não foi encontrado.
        """
        produto = self.obter_produto(codigo)
        if not produto:
            return False
        produto.valor = novo_valor
        return True

    def criar_pedido(self, cpf: str, cod_produto: int, qtd_max_produtos: int) -> Pedido | None:
        """Cria um pedido com o primeiro produto já adicionado.

        Args:
            cpf: CPF do cliente.
            cod_produto: Código do primeiro produto do pedido.
            qtd_max_produtos: Limite máximo de produtos no pedido.

        Returns:
            Pedido criado ou None se cliente/produto não encontrado.
        """
        cliente = self.obter_cliente(cpf)
        produto = self.obter_produto(cod_produto)
        if not cliente or not produto:
            return None
        pedido = Pedido(cliente=cliente, qtd_max_produtos=qtd_max_produtos)
        if not pedido.adicionar_produto(produto):
            return None
        db.pedidos_por_codigo[pedido.codigo] = pedido
        return pedido

    def alterar_pedido(self, cod_pedido: int, cod_produto: int) -> bool:
        """Adiciona um produto a um pedido existente.

        Args:
            cod_pedido: Código do pedido.
            cod_produto: Código do produto a adicionar.

        Returns:
            True se adicionado, False se pedido/produto inválido ou limite excedido.
        """
        pedido = db.pedidos_por_codigo.get(cod_pedido)
        produto = self.obter_produto(cod_produto)
        if not pedido or not produto:
            return False
        return pedido.adicionar_produto(produto)

    def finalizar_pedido(self, cod_pedido: int) -> float | None:
        """Finaliza um pedido e retorna o total calculado.

        Args:
            cod_pedido: Código do pedido.

        Returns:
            Total do pedido ou None se não encontrado.
        """
        pedido = db.pedidos_por_codigo.get(cod_pedido)
        if not pedido:
            return None
        return pedido.finalizar()

    def obter_pedido(self, cod_pedido: int) -> Pedido | None:
        """Busca um pedido pelo código.

        Returns:
            Pedido encontrado ou None.
        """
        return db.pedidos_por_codigo.get(cod_pedido)

    def cancelar_pedido(self, cod_pedido: int) -> bool:
        """Cancela um pedido existente, desde que não esteja finalizado ou já cancelado.

        Returns:
            True se cancelado com sucesso, False caso contrário.
        """
        pedido = db.pedidos_por_codigo.get(cod_pedido)
        if pedido is None:
            return False
        return pedido.cancelar()

    def listar_pedidos_cancelados(self) -> list[Pedido]:
        """Retorna todos os pedidos com estado cancelado.

        Returns:
            Lista de pedidos cancelados.
        """
        pedidos = list(db.pedidos_por_codigo.values())
        return [p for p in pedidos if p.esta_cancelado]

    def adicionar_observacao(self, cod_pedido: int, observacao: str) -> bool:
        """Adiciona ou substitui a observação de um pedido.

        Args:
            cod_pedido: Código do pedido.
            observacao: Texto da observação.

        Returns:
            True se registrada, False se pedido não encontrado ou inválido.
        """
        pedido = db.pedidos_por_codigo.get(cod_pedido)
        if pedido is None:
            return False
        return pedido.adicionar_observacao(observacao)

    def buscar_observacao_pedido(self, cod_pedido: int) -> Pedido | None:
        """Busca um pedido para retornar sua observação.

        Returns:
            Pedido encontrado ou None.
        """
        return db.pedidos_por_codigo.get(cod_pedido)


service = LanchoneteService()