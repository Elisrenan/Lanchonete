# Aula 08 (v2): Persistência Real com Tortoise ORM + SQLite

## O que é um ORM?

ORM significa **Object-Relational Mapper** (Mapeador Objeto-Relacional).

Em vez de escrever SQL diretamente, você define **classes Python** que representam
tabelas do banco. O ORM traduz operações nessas classes para SQL automaticamente.

```
SEM ORM:
  cursor.execute("INSERT INTO clientes (cpf, nome) VALUES (?, ?)", (cpf, nome))

COM ORM:
  await ClienteModel.create(cpf=cpf, nome=nome)
```

Benefícios:
- Código mais legível e orientado a objetos
- Troca de banco de dados sem reescrever queries
- Validações e relacionamentos declarativos

---

## Por que Tortoise ORM?

O Tortoise ORM é o ORM mais adequado para aplicações **FastAPI/asyncio** porque:

| Característica | Tortoise ORM | SQLAlchemy (síncrono) |
|---|---|---|
| Operações de banco | todas `async` | síncronas (requer extensão async) |
| Integração FastAPI | nativa via `register_tortoise` | requer configuração manual |
| Sintaxe | inspirada no Django ORM | SQL Expression Language própria |

---

## Instalação

```bash
pip install tortoise-orm aiosqlite
```

- `tortoise-orm` — o ORM em si
- `aiosqlite` — driver assíncrono para SQLite (necessário para `sqlite://`)

---

## Definindo Models

Um **Model** é uma classe Python que representa uma tabela no banco.
Cada atributo de classe representa uma coluna.

```python
# infrastructure/tortoise/models.py
from tortoise import fields
from tortoise.models import Model

class ClienteModel(Model):
    cpf  = fields.CharField(primary_key=True, max_length=14)
    nome = fields.CharField(max_length=100, default="")

    class Meta:
        table = "clientemodel"
```

### Tipos de campos mais comuns

| Campo | Tipo Python | Uso |
|---|---|---|
| `CharField` | `str` | textos com tamanho máximo |
| `IntField` | `int` | inteiros |
| `FloatField` | `float` | decimais |
| `BooleanField` | `bool` | verdadeiro/falso |
| `DatetimeField` | `datetime` | data e hora |

### Chave primária autoincrement

```python
class PedidoModel(Model):
    codigo = fields.IntField(primary_key=True)   # SQLite gera o valor automaticamente
    cpf_cliente = fields.CharField(max_length=14)
    qtd_max_produtos = fields.IntField()
    estaEntregue = fields.BooleanField(default=False)
    esta_cancelado = fields.BooleanField(default=False)
    observacao = fields.CharField(max_length=200, default="")
```

> Quando `primary_key=True` em um `IntField`, o SQLite gera o valor
> automaticamente (autoincrement) — você não precisa informar o código ao criar.

---

## Configurando o Tortoise ORM

A configuração fica em um dicionário Python centralizado:

```python
# infrastructure/tortoise/config.py
TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://lanchonete.db"   # arquivo na raiz do projeto
    },
    "apps": {
        "models": {
            "models": ["infrastructure.tortoise.models"],  # onde estão os Models
            "default_connection": "default",
        }
    },
}
```

### Formato das connection strings

| Banco | String de conexão |
|---|---|
| SQLite (arquivo) | `sqlite://lanchonete.db` |
| SQLite (memória) | `sqlite://:memory:` |
| PostgreSQL | `postgres://user:pass@host:5432/db` |
| MySQL | `mysql://user:pass@host:3306/db` |

---

## Integrando ao FastAPI com register_tortoise

O `register_tortoise` conecta o ciclo de vida da aplicação FastAPI ao Tortoise:
inicializa a conexão quando a app sobe e fecha quando ela para.

```python
# main.py
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from infrastructure.tortoise.config import TORTOISE_ORM

app = FastAPI()

# ... inclusão de routers ...

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,       # cria as tabelas automaticamente se não existirem
    add_exception_handlers=True, # trata erros do ORM com respostas HTTP adequadas
)
```

> Com `generate_schemas=True`, ao subir a aplicação pela primeira vez o arquivo
> `lanchonete.db` é criado e todas as tabelas são geradas automaticamente.

---

## Operações CRUD com Tortoise

### CREATE — criar registro

```python
cliente = await ClienteModel.create(cpf="11122233344", nome="João")
```

### CREATE ou UPDATE — upsert

```python
# Se não existir, cria. Se existir, atualiza.
await ClienteModel.update_or_create(
    defaults={"nome": nome},
    cpf=cpf,
)
```

### READ — buscar por chave primária

```python
cliente = await ClienteModel.get_or_none(cpf="11122233344")
# retorna None se não encontrado (em vez de levantar exceção)
```

### READ — buscar múltiplos com filtro

```python
cancelados = await PedidoModel.filter(esta_cancelado=True).all()
```

### UPDATE — atualizar campo

```python
pedido = await PedidoModel.get_or_none(codigo=1)
if pedido:
    pedido.estaEntregue = True
    await pedido.save()
```

### DELETE — excluir

```python
await ClienteModel.filter(cpf="11122233344").delete()
```

---

## Padrão Repository com Tortoise

O **Repository Pattern** isola o acesso ao banco do resto da aplicação.
O serviço não conhece o Tortoise — ele só chama métodos do repositório.

```
Rota (FastAPI)
  ↓ chama
Serviço (regras de negócio)
  ↓ chama
Repositório (acesso ao banco)
  ↓ usa
Tortoise ORM → SQLite
```

### Exemplo: ClienteRepoTortoise

```python
# repositories/tortoise/cliente_repo.py
from infrastructure.tortoise.models import ClienteModel
from domain.cliente import Cliente

class ClienteRepoTortoise:

    async def get(self, cpf: str) -> Cliente | None:
        model = await ClienteModel.get_or_none(cpf=cpf)
        if not model:
            return None
        return Cliente(cpf=model.cpf, nome=model.nome)   # ORM → Domínio

    async def save(self, cliente: Cliente) -> None:
        await ClienteModel.update_or_create(
            defaults={"nome": cliente.nome},
            cpf=cliente.cpf,
        )
```

### Por que converter ORM Model → Domínio?

O Model ORM (`ClienteModel`) é um objeto ligado ao banco — ele carrega metadados
do Tortoise, estado de conexão, etc. A entidade de domínio (`Cliente`) é um
objeto Python puro, sem dependência de infraestrutura.

Manter a separação garante que o domínio possa ser testado sem banco de dados.

---

## Injeção de dependência no FastAPI

Os repositórios e o serviço são injetados nas rotas via `Depends`:

```python
# app/deps.py
from services.lanchonete_service import LanchoneteService
from repositories.tortoise.cliente_repo import ClienteRepoTortoise
from repositories.tortoise.produto_repo import ProdutoRepoTortoise
from repositories.tortoise.pedido_repo import PedidoRepoTortoise

def get_service_tortoise() -> LanchoneteService:
    return LanchoneteService(
        ClienteRepoTortoise(),
        ProdutoRepoTortoise(),
        PedidoRepoTortoise(),
    )
```

```python
# api/routes/clientes.py
from fastapi import APIRouter, Depends
from app.deps import get_service_tortoise

router = APIRouter(prefix="/clientes")

@router.post("")
async def criar(payload: ClienteCreate, svc = Depends(get_service_tortoise)):
    cliente = await svc.criar_cliente(payload.cpf, payload.nome)
    return ClienteOut(cpf=cliente.cpf, nome=cliente.nome)
```

> A cada requisição, o FastAPI chama `get_service_tortoise()` e injeta
> o serviço na função. Isso facilita a troca da implementação (ex: trocar
> SQLite por PostgreSQL) sem alterar as rotas.

---

## Estrutura de arquivos adicionados

```
infrastructure/
    tortoise/
        __init__.py
        config.py        ← configuração da conexão com o banco
        models.py        ← definição das tabelas (ClienteModel, ProdutoModel, ...)

repositories/
    tortoise/
        __init__.py
        cliente_repo.py  ← CRUD de clientes via Tortoise
        produto_repo.py  ← CRUD de produtos via Tortoise
        pedido_repo.py   ← CRUD de pedidos e itens via Tortoise

app/
    __init__.py
    deps.py              ← factory de dependência para o FastAPI
```

---

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
