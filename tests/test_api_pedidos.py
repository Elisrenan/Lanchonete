# =============================================================================
# test_api_pedidos.py — Teste de integração do fluxo completo de pedidos
# =============================================================================
#
# Este arquivo contém um teste de ponta a ponta (end-to-end): simulamos
# todo o ciclo de vida de um pedido passando pela API, do cadastro dos
# dados até a finalização com cálculo do total.
#
# Com a migração para Tortoise ORM async, as chamadas ao client usam `await`
# e as funções de teste são declaradas como `async def`.
# =============================================================================


async def test_fluxo_completo_pedido(client):
    """Simula o ciclo de vida completo de um pedido via API.

    Etapas do fluxo:
        1. Criar um cliente
        2. Criar dois produtos com tipos diferentes
        3. Abrir um pedido com o primeiro produto
        4. Adicionar o segundo produto ao pedido
        5. Finalizar o pedido e verificar o total

    Dados utilizados:
        - Produto 1: tipo 1, valor R$10, desconto 10% → preço final R$9,00
        - Produto 2: tipo 2, valor R$20, desconto 10% → preço ignorado → R$20,00
        - Total esperado: 9.0 + 20.0 = 29.0

    Por que salvar o código do pedido?
        A API gera o código automaticamente e o retorna na criação.
        Precisamos desse código para referenciar o pedido nas chamadas
        seguintes (adicionar item e finalizar).
    """
    # 1. Cria o cliente que fará o pedido
    await client.post("/clientes", json={"cpf": "11122233344", "nome": "Cliente X"})

    # 2. Cria os produtos disponíveis no cardápio
    #    Produto 1 (tipo 1): desconto será aplicado
    #    Produto 2 (tipo 2): desconto será ignorado pela regra de negócio
    await client.post("/produtos", json={"codigo": 1, "valor": 10, "tipo": 1, "desconto_percentual": 10})
    await client.post("/produtos", json={"codigo": 2, "valor": 20, "tipo": 2, "desconto_percentual": 10})

    # 3. Abre o pedido com o primeiro produto já incluído
    r = await client.post("/lanchonete/pedidos", json={"cpf": "11122233344", "cod_produto": 1, "qtd_max_produtos": 10})
    assert r.status_code == 200
    cod_pedido = r.json()["codigo"]  # guarda o código para usar nas próximas chamadas

    # 4. Adiciona o segundo produto ao pedido já existente
    r2 = await client.put(f"/lanchonete/pedidos/{cod_pedido}/itens", json={"cod_produto": 2})
    assert r2.status_code == 200

    # 5. Finaliza o pedido e valida o total calculado
    r3 = await client.post(f"/lanchonete/pedidos/{cod_pedido}/finalizar")
    assert r3.status_code == 200
    assert r3.json()["total"] == 29.0