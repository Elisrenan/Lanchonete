from tortoise import fields
from tortoise.models import Model


class ClienteModel(Model):
    cpf = fields.CharField(pk=True, max_length=14)
    nome = fields.CharField(max_length=120, default="")


class ProdutoModel(Model):
    codigo = fields.IntField(pk=True)
    valor = fields.FloatField()
    tipo = fields.IntField()
    desconto_percentual = fields.FloatField(default=0.0)


class PedidoModel(Model):
    codigo = fields.IntField(pk=True)
    cpf_cliente = fields.CharField(max_length=14)
    qtd_max_produtos = fields.IntField()
    estaEntregue = fields.BooleanField(default=False)
    esta_cancelado = fields.BooleanField(default=False)
    observacao = fields.CharField(max_length=200, default="")


class PedidoItemModel(Model):
    id = fields.IntField(pk=True)
    pedido_codigo = fields.IntField()
    produto_codigo = fields.IntField()
