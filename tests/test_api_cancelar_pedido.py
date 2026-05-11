async def test_deve_cancelar_pedido_com_sucesso(client):
    """Verifica o fluxo feliz do cancelamento de pedido.

    Cenário:
        Um cliente e um produto são cadastrados, um pedido é criado e
        em seguida o endpoint PATCH /cancelar é chamado.

    Resultado esperado:
        - Status HTTP 200
        - Corpo com ok=True e mensagem de confirmação
    """
    await client.post("/clientes", json={"cpf": "12345678900", "nome": "Joao"})
    await client.post("/produtos", json={"codigo": 1, "valor": 10.0, "tipo": 2})
    r = await client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido = r.json()["codigo"]

    response = await client.patch(f"/lanchonete/pedidos/{cod_pedido}/cancelar")

    assert response.status_code == 200

    data = response.json()
    assert data["ok"] is True
    assert data["mensagem"] == "Pedido cancelado com sucesso"


async def test_nao_deve_cancelar_pedido_inexistente(client):
    """Garante que tentar cancelar um pedido inexistente retorna erro.

    Cenário:
        Nenhum pedido é criado. O endpoint é chamado com um código
        que não existe no repositório (999).

    Resultado esperado:
        - Status HTTP 400
        - Mensagem de erro indicando que o pedido não foi encontrado
    """
    response = await client.patch("/lanchonete/pedidos/999/cancelar")

    assert response.status_code == 400

    data = response.json()
    assert data["detail"] == "Pedido não encontrado ou não pode ser cancelado"


async def test_nao_deve_cancelar_pedido_finalizado(client):
    """Garante que um pedido já finalizado não pode ser cancelado.

    Cenário:
        Um pedido é criado e finalizado via POST /finalizar.
        Em seguida, tenta-se cancelá-lo.

    Regra de negócio:
        Um pedido finalizado (entregue) não pode ser revertido.

    Resultado esperado:
        - Status HTTP 400
        - Mesma mensagem de erro do caso de pedido inexistente,
          pois a API não distingue o motivo da recusa
    """
    await client.post("/clientes", json={"cpf": "12345678900", "nome": "Joao"})
    await client.post("/produtos", json={"codigo": 1, "valor": 10.0, "tipo": 2})
    r = await client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido = r.json()["codigo"]
    await client.post(f"/lanchonete/pedidos/{cod_pedido}/finalizar")

    response = await client.patch(f"/lanchonete/pedidos/{cod_pedido}/cancelar")

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Pedido não encontrado ou não pode ser cancelado"


async def test_deve_listar_pedidos_cancelados(client):
    """Verifica que o endpoint de listagem retorna apenas pedidos cancelados.

    Cenário:
        Um pedido é criado e cancelado. Em seguida, GET /cancelados
        é chamado para consultar a lista.

    Resultado esperado:
        - Status HTTP 200
        - Resposta é uma lista com pelo menos um item
        - O pedido retornado possui esta_cancelado=True
    """
    await client.post("/clientes", json={"cpf": "12345678900", "nome": "Joao"})
    await client.post("/produtos", json={"codigo": 1, "valor": 10.0, "tipo": 2})
    r = await client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido = r.json()["codigo"]
    await client.patch(f"/lanchonete/pedidos/{cod_pedido}/cancelar")

    response = await client.get("/lanchonete/pedidos/cancelados")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["esta_cancelado"] is True
