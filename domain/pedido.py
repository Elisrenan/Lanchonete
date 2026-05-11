from typing import List
from domain.cliente import Cliente
from domain.produto import Produto


class Pedido:
    """Representa um pedido realizado por um cliente.

    O código do pedido é gerado automaticamente via sequencial estático.

    Attributes:
        cliente: Cliente que realizou o pedido.
        qtd_max_produtos: Limite máximo de produtos que o pedido pode conter.
        listaProdutos: Lista dos produtos adicionados ao pedido.
        esta_entregue: Indica se o pedido foi finalizado/entregue.
    """

    _seq = 1

    def __init__(self, cliente: Cliente, qtd_max_produtos: int):
        """Inicializa um novo pedido.

        Args:
            cliente: Cliente dono do pedido.
            qtd_max_produtos: Número máximo de produtos permitidos.

        Raises:
            ValueError: Se qtd_max_produtos for menor ou igual a zero.
        """
        self._codigo = Pedido._seq
        Pedido._seq += 1
        self.cliente = cliente
        self.qtd_max_produtos = int(qtd_max_produtos)
        self.listaProdutos: List[Produto] = []
        self.esta_entregue: bool = False
        self.esta_cancelado: bool = False

        if self.qtd_max_produtos <= 0:
            raise ValueError("Quantidade máxima deve ser maior que zero")

    @property
    def codigo(self) -> int:
        """Código único e imutável do pedido."""
        return self._codigo

    def adicionar_produto(self, produto: Produto) -> bool:
        """Adiciona um produto ao pedido, respeitando o limite máximo.

        Args:
            produto: Produto a ser adicionado.

        Returns:
            True se adicionado com sucesso, False se o limite já foi atingido.
        """
        if len(self.listaProdutos) >= self.qtd_max_produtos:
            return False
        self.listaProdutos.append(produto)
        return True

    def finalizar(self) -> float:
        """Finaliza o pedido, marca como entregue e calcula o total.

        Returns:
            Soma dos preços finais de todos os produtos.
        """
        self.esta_entregue = True
        total = 0.0
        for p in self.listaProdutos:
            total += p.preco_final()
        return float(total)

    def cancelar(self) -> bool:
        if self.esta_entregue:
            return False

        if self.esta_cancelado:
            return False

        self.esta_cancelado = True
        return True

    def total_se_finalizado(self) -> float:
        """Retorna o total do pedido apenas se já estiver finalizado.

        Returns:
            Total calculado se entregue, 0.0 caso contrário.
        """
        if not self.esta_entregue:
            return 0.0
        total = 0.0
        for p in self.listaProdutos:
            total += p.preco_final()
        return float(total)
