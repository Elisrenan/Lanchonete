async def test_deve_adicionar_observacao(client):
    """Verifica o fluxo feliz de adição de observação.

    Cenário:
        Um cliente, produto e pedido são criados. A observação é enviada
        via POST /{cod_pedido}/observacao.

    Resultado esperado:
        - Status HTTP 200
        - Corpo com ok=True e mensagem de confirmação
    """
    await client.post("/clientes", json={"cpf": "12345678900", "nome": "Joao"})
    await client.post("/produtos", json={"codigo": 1, "valor": 10.0, "tipo": 2})
    r = await client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido = r.json()["codigo"]

    response = await client.post(
        f"/lanchonete/pedidos/{cod_pedido}/observacao",
        json={"observacao": "Sem cebola"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["ok"] is True
    assert data["mensagem"] == "Observação adicionada com sucesso"


async def test_nao_deve_aceitar_observacao_vazia(client):
    """Garante que uma observação vazia é rejeitada.

    Cenário:
        Um pedido é criado e o endpoint é chamado com observacao="".

    Regra de negócio:
        Observações vazias ou compostas só de espaços não são permitidas.

    Resultado esperado:
        - Status HTTP 400
        - Mensagem de erro indicando pedido inválido
    """
    await client.post("/clientes", json={"cpf": "12345678900", "nome": "Joao"})
    await client.post("/produtos", json={"codigo": 1, "valor": 10.0, "tipo": 2})
    r = await client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido = r.json()["codigo"]

    response = await client.post(
        f"/lanchonete/pedidos/{cod_pedido}/observacao",
        json={"observacao": ""},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Pedido não encontrado ou inválido"


async def test_nao_deve_adicionar_observacao_em_pedido_finalizado(client):
    """Garante que pedido finalizado não aceita observação.

    Cenário:
        Um pedido é criado e finalizado. Em seguida, tenta-se adicionar
        uma observação.

    Regra de negócio:
        Após finalização, o pedido não pode ser alterado.

    Resultado esperado:
        - Status HTTP 400
        - Mensagem de erro indicando pedido inválido
    """
    await client.post("/clientes", json={"cpf": "12345678900", "nome": "Joao"})
    await client.post("/produtos", json={"codigo": 1, "valor": 10.0, "tipo": 2})
    r = await client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido = r.json()["codigo"]
    await client.post(f"/lanchonete/pedidos/{cod_pedido}/finalizar")

    response = await client.post(
        f"/lanchonete/pedidos/{cod_pedido}/observacao",
        json={"observacao": "Sem molho"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Pedido não encontrado ou inválido"


async def test_deve_buscar_observacao_pedido(client):
    """Verifica que a observação registrada pode ser consultada.

    Cenário:
        Um pedido é criado, uma observação é adicionada e em seguida
        GET /{cod_pedido}/observacao é chamado.

    Resultado esperado:
        - Status HTTP 200
        - Corpo com o código do pedido e o texto da observação registrada
    """
    await client.post("/clientes", json={"cpf": "12345678900", "nome": "Joao"})
    await client.post("/produtos", json={"codigo": 1, "valor": 10.0, "tipo": 2})
    r = await client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido = r.json()["codigo"]
    await client.post(
        f"/lanchonete/pedidos/{cod_pedido}/observacao",
        json={"observacao": "Carne ao ponto"},
    )

    response = await client.get(f"/lanchonete/pedidos/{cod_pedido}/observacao")

    assert response.status_code == 200

    data = response.json()
    assert data["codigo"] == cod_pedido
    assert data["observacao"] == "Carne ao ponto"
