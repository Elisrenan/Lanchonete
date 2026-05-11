# =============================================================================
# models.py — Modelos Tortoise ORM (mapeamento objeto-relacional)
# =============================================================================
#
# Cada classe herda de Model e representa uma tabela no banco de dados.
# O Tortoise usa os campos declarados para criar as colunas automaticamente
# quando generate_schemas=True (ou via migrations com Aerich).
#
# IMPORTANTE: estes modelos NÃO são entidades de domínio. Eles só existem
# na camada de infraestrutura. Os repositórios convertem entre Model ↔ domínio.
# =============================================================================

from tortoise import fields
from tortoise.models import Model


class ClienteModel(Model):
    """Tabela de clientes no banco de dados.

    Campos:
        cpf:  Chave primária — CPF do cliente (formato livre, máx. 14 chars).
        nome: Nome completo do cliente. Padrão vazio para cadastros parciais.
    """
    cpf = fields.CharField(primary_key=True, max_length=14)
    nome = fields.CharField(max_length=120, default="")


class ProdutoModel(Model):
    """Tabela de produtos disponíveis no cardápio.

    Campos:
        codigo:               Chave primária — identificador único do produto.
        valor:                Preço base (sem desconto aplicado).
        tipo:                 Categoria: 1 = com desconto | 2 = sem desconto.
        desconto_percentual:  Percentual a descontar quando tipo == 1.
    """
    codigo = fields.IntField(primary_key=True)
    valor = fields.FloatField()
    tipo = fields.IntField()
    desconto_percentual = fields.FloatField(default=0.0)


class PedidoModel(Model):
    """Tabela de pedidos realizados pelos clientes.

    O código é gerado automaticamente pelo SQLite (autoincrement).
    Os produtos do pedido ficam em PedidoItemModel (relação 1→N).

    Campos:
        codigo:          Chave primária — ID gerado pelo banco.
        cpf_cliente:     CPF do cliente que realizou o pedido.
        qtd_max_produtos: Limite máximo de itens permitidos no pedido.
        estaEntregue:    True após finalizar/entregar o pedido.
        esta_cancelado:  True se o pedido foi cancelado antes da entrega.
        observacao:      Instrução livre do cliente (ex: "sem cebola").
    """
    codigo = fields.IntField(primary_key=True)
    cpf_cliente = fields.CharField(max_length=14)
    qtd_max_produtos = fields.IntField()
    estaEntregue = fields.BooleanField(default=False)
    esta_cancelado = fields.BooleanField(default=False)
    observacao = fields.CharField(max_length=200, default="")


class PedidoItemModel(Model):
    """Tabela de itens de um pedido (relação pedido ↔ produto).

    Cada linha representa um produto adicionado a um pedido.
    Um mesmo produto pode aparecer múltiplas vezes se adicionado mais de uma vez.

    Campos:
        id:             Chave primária autoincrement.
        pedido_codigo:  Referência ao código do PedidoModel.
        produto_codigo: Referência ao código do ProdutoModel.
    """
    id = fields.IntField(primary_key=True)
    pedido_codigo = fields.IntField()
    produto_codigo = fields.IntField()
