"""
seed.py — Povoa o banco de dados lanchonete.db com dados de exemplo.

Os dados seguem exatamente os cenários dos testes automatizados, permitindo
explorar a API manualmente (via Swagger UI ou curl) com um estado inicial
já conhecido.

Uso:
    python seed.py

Pré-requisito:
    A aplicação deve estar parada (não é necessário subir o FastAPI).
    O banco lanchonete.db será criado/atualizado na raiz do projeto.
"""

import asyncio
from tortoise import Tortoise
from infrastructure.tortoise.config import TORTOISE_ORM
from infrastructure.tortoise.models import (
    ClienteModel,
    ProdutoModel,
    PedidoModel,
    PedidoItemModel,
)


async def seed():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    print("Limpando dados anteriores...")
    await PedidoItemModel.all().delete()
    await PedidoModel.all().delete()
    await ProdutoModel.all().delete()
    await ClienteModel.all().delete()

    # ------------------------------------------------------------------
    # Clientes
    # ------------------------------------------------------------------
    print("Criando clientes...")
    clientes = [
        {"cpf": "11122233344", "nome": "Cliente X"},
        {"cpf": "12345678900", "nome": "Joao"},
        {"cpf": "99988877766", "nome": "Maria"},
    ]
    for c in clientes:
        await ClienteModel.create(**c)
        print(f"  + Cliente: {c['nome']} ({c['cpf']})")

    # ------------------------------------------------------------------
    # Produtos
    # ------------------------------------------------------------------
    print("Criando produtos...")
    produtos = [
        # tipo 1 → desconto percentual aplicado no total
        {"codigo": 1, "valor": 10.0, "tipo": 1, "desconto_percentual": 10.0},
        # tipo 2 → desconto ignorado
        {"codigo": 2, "valor": 20.0, "tipo": 2, "desconto_percentual": 10.0},
        {"codigo": 3, "valor": 15.0, "tipo": 2, "desconto_percentual": 0.0},
    ]
    for p in produtos:
        await ProdutoModel.create(**p)
        print(f"  + Produto #{p['codigo']}: R${p['valor']} (tipo {p['tipo']})")

    # ------------------------------------------------------------------
    # Pedido 1 — fluxo completo (finalizado)
    #   Cliente X compra produto 1 (tipo 1, R$9,00 c/ desconto)
    #   e produto 2 (tipo 2, R$20,00 sem desconto)
    #   Total esperado: 9.0 + 20.0 = 29.0
    # ------------------------------------------------------------------
    print("Criando pedido 1 (finalizado)...")
    pedido1 = await PedidoModel.create(
        cpf_cliente="11122233344",
        qtd_max_produtos=10,
        estaEntregue=True,
        esta_cancelado=False,
        observacao="",
    )
    await PedidoItemModel.create(pedido_codigo=pedido1.codigo, produto_codigo=1)
    await PedidoItemModel.create(pedido_codigo=pedido1.codigo, produto_codigo=2)
    print(f"  + Pedido #{pedido1.codigo} finalizado — total: R$29,00")

    # ------------------------------------------------------------------
    # Pedido 2 — cancelado
    #   Joao abre um pedido e cancela antes de finalizar
    # ------------------------------------------------------------------
    print("Criando pedido 2 (cancelado)...")
    pedido2 = await PedidoModel.create(
        cpf_cliente="12345678900",
        qtd_max_produtos=5,
        estaEntregue=False,
        esta_cancelado=True,
        observacao="",
    )
    await PedidoItemModel.create(pedido_codigo=pedido2.codigo, produto_codigo=1)
    print(f"  + Pedido #{pedido2.codigo} cancelado")

    # ------------------------------------------------------------------
    # Pedido 3 — em aberto com observação
    #   Maria faz pedido com observação registrada
    # ------------------------------------------------------------------
    print("Criando pedido 3 (em aberto, com observação)...")
    pedido3 = await PedidoModel.create(
        cpf_cliente="99988877766",
        qtd_max_produtos=5,
        estaEntregue=False,
        esta_cancelado=False,
        observacao="Sem cebola",
    )
    await PedidoItemModel.create(pedido_codigo=pedido3.codigo, produto_codigo=3)
    print(f"  + Pedido #{pedido3.codigo} em aberto — observação: 'Sem cebola'")

    await Tortoise.close_connections()
    print("\nSeed concluído com sucesso!")
    print("Suba a aplicação com:  fastapi dev main.py")
    print("Acesse o Swagger em:   http://127.0.0.1:8000/docs")


if __name__ == "__main__":
    asyncio.run(seed())
