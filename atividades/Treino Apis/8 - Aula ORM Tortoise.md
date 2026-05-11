# Aula 08 (v2): Testando APIs com Tortoise ORM e pytest-asyncio

## O que mudou após a migração para ORM?

Antes desta aula, a aplicação guardava tudo em memória (`MemoryDB`). Os testes
podiam simplesmente limpar um dicionário entre cada execução. Com o Tortoise ORM,
os dados vão para um banco de dados real — e isso muda como os testes funcionam.

**Três problemas novos:**

| Problema | Causa | Solução adotada |
|---|---|---|
| Métodos são `async` | Tortoise exige `await` para qualquer operação de banco | `pytest-asyncio` com `asyncio_mode = auto` |
| Estado persiste entre testes | SQLite em arquivo acumula registros | SQLite `:memory:` — banco destruído ao fechar |
| Event loop conflita | `TestClient` cria seu próprio loop | `httpx.AsyncClient` com `ASGITransport` |

---

## Instalação

```bash
pip install pytest-asyncio httpx
```

> O `httpx` já vem como dependência do FastAPI. O `pytest-asyncio` é o novo
> pacote necessário para rodar testes assíncronos com o pytest.

---

## Configuração: pytest.ini

```ini
[pytest]
pythonpath = .
asyncio_mode = auto
```

O `asyncio_mode = auto` instrui o pytest-asyncio a tratar **automaticamente**
toda função `async def test_*` como um coroutine assíncrono, sem precisar
decorar cada teste com `@pytest.mark.asyncio`.

Funções de teste síncronas (`def test_*`) continuam funcionando normalmente —
o modo `auto` não as afeta.

---

## O que é pytest-asyncio?

O pytest, por padrão, só consegue executar funções síncronas. Quando uma função
de teste é `async def`, ele não sabe como executá-la.

O `pytest-asyncio` resolve isso: ele cria um event loop para o conjunto de
testes e executa cada `async def test_*` como uma coroutine dentro desse loop.

```python
# SEM pytest-asyncio → erro: coroutine was never awaited
async def test_exemplo():
    ...

# COM pytest-asyncio (asyncio_mode = auto) → funciona
async def test_exemplo():
    r = await client.get("/health")
    assert r.status_code == 200
```

---

## Fixture: init_test_db

Esta fixture substitui o antigo `reset_memory_db`. Em vez de limpar um
dicionário, ela inicializa o Tortoise com um banco SQLite em memória.

```python
@pytest_asyncio.fixture(autouse=True)
async def init_test_db():
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["infrastructure.tortoise.models"]}
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()
```

### Por que `sqlite://:memory:`?

O SQLite aceita o caminho especial `:memory:` que cria o banco inteiramente
dentro da RAM, sem criar nenhum arquivo no disco. A conexão existe apenas
enquanto está aberta: quando `close_connections()` é chamado, o banco some.

Resultado: cada teste começa com tabelas **vazias e recém-criadas**.

### Por que `@pytest_asyncio.fixture` e não `@pytest.fixture`?

O `@pytest_asyncio.fixture` é a forma explícita de declarar uma fixture
assíncrona para o pytest-asyncio. Dentro dela, `await` funciona normalmente.

### Fluxo do `yield`

```
ANTES do yield  →  setup:    init + generate_schemas
                →  o teste roda aqui
DEPOIS do yield →  teardown: close_connections (banco destruído)
```

---

## Fixture: client

```python
@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
```

### Por que `AsyncClient` em vez de `TestClient`?

O `TestClient` do FastAPI é **síncrono**: ele cria internamente um event loop
para despachar as requisições. Isso causa conflito porque o pytest-asyncio
**já tem um event loop ativo** (o mesmo que roda os testes e o Tortoise).

O `AsyncClient` com `ASGITransport` não cria um event loop novo: ele despacha
as requisições diretamente no event loop **existente** do pytest-asyncio.

```
pytest-asyncio (event loop)
├── init_test_db fixture   → Tortoise conectado a :memory:
├── client fixture         → AsyncClient no mesmo loop
└── test_xxx               → await client.post(...) → mesmo loop → mesmo banco ✅
```

### Como o ASGITransport funciona?

O ASGI (Asynchronous Server Gateway Interface) é o protocolo que o FastAPI
usa internamente. O `ASGITransport` implementa esse protocolo simulando
uma conexão HTTP sem precisar de sockets de rede reais.

```python
# Sem ASGITransport (porta de rede real):
# cliente → localhost:8000 → servidor uvicorn → app

# Com ASGITransport (sem rede):
# cliente → ASGITransport → app (direto, na memória)
```

---

## Escrevendo testes async

### Antes (sync)

```python
def test_post_e_get_cliente(client):
    response = client.post("/clientes", json={"cpf": "111", "nome": "X"})
    assert response.status_code == 200
```

### Depois (async)

```python
async def test_post_e_get_cliente(client):
    response = await client.post("/clientes", json={"cpf": "111", "nome": "X"})
    assert response.status_code == 200
```

As únicas mudanças são:
1. `def` → `async def`
2. `client.post(...)` → `await client.post(...)`

O corpo do teste, os `assert` e a lógica de negócio são idênticos.

---

## Testes que NÃO precisam mudar

Testes **unitários de domínio** (`test_domain_produto.py`, `test_domain_pedido.py`)
testam classes Python puras — sem banco, sem API. Eles continuam **síncronos**:

```python
# Não precisa ser async — não acessa banco nem API
def test_produto_tipo_1_aplica_desconto():
    p = Produto(codigo=1, valor=10, tipo=1, desconto_percentual=10)
    assert p.preco_final() == 9.0
```

Regra prática: **se o teste não usa o fixture `client`, provavelmente não
precisa ser `async`**.

---

## Mapa dos testes do projeto

```
tests/
│
├── conftest.py                   # fixtures: init_test_db, client (async)
│
├── test_domain_produto.py        # unitários — regras de desconto (sync)
│   ├── test_produto_tipo_1_aplica_desconto
│   ├── test_produto_tipo_2_nao_aplica_desconto
│   └── test_produto_sem_desconto
│
├── test_domain_pedido.py         # unitários — regras de pedido (sync)
│   ├── test_pedido_limite_itens
│   ├── test_pedido_total_se_nao_finalizado_retorna_0
│   └── test_pedido_finalizar_calcula_total_com_regras
│
├── test_api_clientes.py          # integração — endpoints de clientes (async)
│   ├── test_post_e_get_cliente
│   └── test_get_cliente_inexistente
│
├── test_api_pedidos.py           # end-to-end — ciclo completo (async)
│   └── test_fluxo_completo_pedido
│
├── test_api_cancelar_pedido.py   # integração — cancelamento (async)
│   ├── test_deve_cancelar_pedido_com_sucesso
│   ├── test_nao_deve_cancelar_pedido_inexistente
│   ├── test_nao_deve_cancelar_pedido_finalizado
│   └── test_deve_listar_pedidos_cancelados
│
└── test_api_observacao_pedido.py # integração — observações (async)
    ├── test_deve_adicionar_observacao
    ├── test_nao_deve_aceitar_observacao_vazia
    ├── test_nao_deve_adicionar_observacao_em_pedido_finalizado
    └── test_deve_buscar_observacao_pedido
```

---

## Como rodar os testes

Na raiz do projeto (com o venv ativado):

```bash
pytest -v
```

Para rodar apenas os testes de API:

```bash
pytest tests/test_api_clientes.py -v
```

Para rodar apenas os testes unitários de domínio:

```bash
pytest tests/test_domain_produto.py tests/test_domain_pedido.py -v
```

Para rodar um único teste:

```bash
pytest tests/test_api_pedidos.py::test_fluxo_completo_pedido -v
```

---

## Pirâmide de testes com ORM

```
        /\
       /E2E\         test_api_pedidos.py (fluxo completo)
      /------\
     / Integr.\      test_api_clientes, cancelar, observacao
    /----------\
   /  Unitários \    test_domain_produto, test_domain_pedido
  /--------------\
```

Com ORM, os testes de integração ficam mais pesados (criam conexão com banco
a cada teste), por isso a base unitária continua sendo a mais importante.

---

## Isolamento e o banco :memory:

Um princípio fundamental: **cada teste deve ser independente**.

Com `sqlite://:memory:`, o isolamento é garantido pelo próprio banco:

```
Teste 1:
  init_test_db → conecta :memory: (banco A)
  test roda → insere dados no banco A
  close_connections → banco A destruído

Teste 2:
  init_test_db → conecta :memory: (banco B — completamente novo)
  test roda → começa vazio ✅
```

Nenhum dado vazou do Teste 1 para o Teste 2.

---

## Atividade prática

Com base no projeto da lanchonete migrado para Tortoise ORM, escreva os
seguintes testes:

### 1. Integração — Produto não encontrado

Crie um teste que chame `GET /produtos/9999` (produto inexistente) e verifique
que o status retornado é `404`.

```python
async def test_get_produto_inexistente(client):
    # escreva aqui
    ...
```

### 2. Integração — Atualizar valor do produto

Crie um produto via `POST /produtos` e em seguida altere seu valor via
`PUT /produtos/{codigo}/valor`. Verifique que:
- O status da alteração é `200`
- O body retornado contém `{"alterou": true}`

### 3. End-to-end — Buscar pedido pelo código

Estenda o fluxo do `test_fluxo_completo_pedido`: após criar o pedido, chame
`GET /lanchonete/pedidos/{cod_pedido}` e verifique que:
- O status é `200`
- O CPF retornado é o mesmo do cliente criado

```python
async def test_buscar_pedido_por_codigo(client):
    # 1. Crie cliente e produto
    # 2. Crie o pedido e salve o codigo
    # 3. GET /lanchonete/pedidos/{cod_pedido}
    # 4. assert status_code == 200
    # 5. assert cpf == "11122233344"
    ...
```

### 4. Integração — CPF vazio deve retornar 400

```python
async def test_criar_cliente_cpf_vazio(client):
    response = await client.post("/clientes", json={"cpf": "", "nome": "X"})
    assert response.status_code == 400
```

### 5. Sad path — Pedido com limite atingido

Crie um pedido com `qtd_max_produtos=1`, adicione um produto na criação e
tente adicionar um segundo via `PUT /itens`. Verifique que o segundo retorna
status `400`.

> **Dica:** O `asyncio_mode = auto` no `pytest.ini` já cuida de tudo.
> Basta escrever `async def test_xxx(client):` e usar `await` nas chamadas.

> **Dica 2:** Quer verificar se uma exception é levantada no domínio?
> Os testes unitários continuam síncronos e usam `pytest.raises`:
> ```python
> import pytest
> from domain.produto import Produto
>
> def test_produto_valor_negativo():
>     with pytest.raises(ValueError):
>         Produto(codigo=1, valor=-5, tipo=1)
> ```
