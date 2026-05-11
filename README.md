# Lanchonete API

API REST para gerenciamento de clientes, produtos e pedidos de uma lanchonete.  
Construída com **FastAPI**, **Tortoise ORM** e **SQLite**, utilizando programação **assíncrona** (`async/await`) em todas as camadas.

---

## Stack

| Tecnologia       | Versão   | Papel                                   |
|------------------|----------|-----------------------------------------|
| Python           | 3.14     | Linguagem principal                     |
| FastAPI          | 0.136+   | Framework web / definição de rotas      |
| Tortoise ORM     | 1.1.7    | ORM assíncrono para acesso ao banco     |
| aiosqlite        | 0.22.1   | Driver async para SQLite                |
| Pydantic         | v2       | Validação de schemas de entrada/saída   |
| pytest           | 9.0+     | Runner de testes                        |
| pytest-asyncio   | 1.3.0    | Suporte a testes assíncronos            |
| httpx            | 0.28+    | Cliente HTTP para testes de integração  |

---

## Configuração do ambiente

### 1. Criar e ativar o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate      # ativar  (Linux/Mac)
# .venv\Scripts\activate       # ativar  (Windows)
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Executar o projeto

```bash
fastapi dev main.py
```

O banco de dados `lanchonete.db` (SQLite) é criado automaticamente na raiz do projeto na primeira execução.  
A documentação interativa (Swagger UI) fica disponível em: <http://127.0.0.1:8000/docs>

---

## Endpoints da API

### Clientes — `/clientes`

| Método | Rota             | Descrição                                  |
|--------|------------------|--------------------------------------------|
| POST   | `/clientes`      | Cria um cliente (ou retorna o existente)   |
| GET    | `/clientes/{cpf}`| Busca um cliente pelo CPF                  |

**POST `/clientes`** — corpo da requisição:
```json
{ "cpf": "111.111.111-11", "nome": "João Silva" }
```

---

### Produtos — `/produtos`

| Método | Rota                      | Descrição                        |
|--------|---------------------------|----------------------------------|
| POST   | `/produtos`               | Cria um produto                  |
| GET    | `/produtos/{codigo}`      | Busca um produto pelo código     |
| PUT    | `/produtos/{codigo}/valor`| Atualiza o valor de um produto   |

**POST `/produtos`** — corpo da requisição:
```json
{ "codigo": 1, "valor": 10.0, "tipo": 1, "desconto_percentual": 10.0 }
```

> Produtos do **tipo 1** aplicam desconto percentual no cálculo do total do pedido.  
> Produtos do **tipo 2** não recebem desconto.

---

### Pedidos — `/lanchonete/pedidos`

| Método | Rota                                  | Descrição                                      |
|--------|---------------------------------------|------------------------------------------------|
| POST   | `/lanchonete/pedidos`                 | Cria um pedido com o primeiro produto          |
| PUT    | `/lanchonete/pedidos/{cod}/itens`     | Adiciona um produto ao pedido                  |
| POST   | `/lanchonete/pedidos/{cod}/finalizar` | Finaliza o pedido e retorna o total            |
| GET    | `/lanchonete/pedidos/{cod}`           | Busca um pedido pelo código                    |
| PATCH  | `/lanchonete/pedidos/{cod}/cancelar`  | Cancela um pedido (somente antes de finalizar) |
| GET    | `/lanchonete/pedidos/cancelados`      | Lista todos os pedidos cancelados              |
| POST   | `/lanchonete/pedidos/{cod}/observacao`| Adiciona/substitui a observação do pedido      |
| GET    | `/lanchonete/pedidos/{cod}/observacao`| Retorna a observação registrada no pedido      |

**POST `/lanchonete/pedidos`** — corpo da requisição:
```json
{ "cpf": "111.111.111-11", "cod_produto": 1, "qtd_max_produtos": 5 }
```

**PUT `/lanchonete/pedidos/{cod}/itens`** — corpo da requisição:
```json
{ "cod_produto": 2 }
```

**POST `/lanchonete/pedidos/{cod}/observacao`** — corpo da requisição:
```json
{ "observacao": "sem cebola, por favor" }
```

---

## Testes

### Rodar os testes

```bash
pytest -v
```

### Resultado atual

```
17 passed in 0.38s
```

| Arquivo de teste                    | Testes | O que cobre                                             |
|-------------------------------------|--------|---------------------------------------------------------|
| `test_domain_produto.py`            | 3      | Regras de desconto por tipo de produto                  |
| `test_domain_pedido.py`             | 3      | Limite de itens, total zerado, cálculo com desconto     |
| `test_api_clientes.py`              | 2      | Criação e busca de clientes via HTTP                    |
| `test_api_pedidos.py`               | 1      | Fluxo completo: criar → adicionar item → finalizar      |
| `test_api_cancelar_pedido.py`       | 4      | Cancelamento: sucesso, pedido inexistente, já finalizado, listagem |
| `test_api_observacao_pedido.py`     | 4      | Observação: adicionar, validar vazio, pedido finalizado, buscar |

> Os testes de API usam banco SQLite **em memória** (`sqlite://:memory:`), isolado por teste.

---

## Estrutura do projeto

```
main.py                          # Ponto de entrada FastAPI + registro do Tortoise ORM
seed.py                          # Script para popular o banco com dados de exemplo
pytest.ini                       # Configuração do pytest (asyncio_mode = auto)
requirements.txt
app/
    deps.py                      # Factory para injeção de dependência (get_service_tortoise)
api/
    routes/
        clientes.py              # Rotas de clientes
        produtos.py              # Rotas de produtos
        pedidos.py               # Rotas de pedidos
        health.py                # Health check
domain/
    cliente.py                   # Entidade Cliente
    produto.py                   # Entidade Produto (com regra de desconto)
    pedido.py                    # Entidade Pedido (com regra de limite e total)
infrastructure/
    tortoise/
        config.py                # Configuração do Tortoise ORM (produção)
        models.py                # Models ORM: ClienteModel, ProdutoModel, PedidoModel, PedidoItemModel
repositories/
    memory.py                    # Repositório em memória (legado / referência)
    tortoise/
        cliente_repo.py          # Repositório de clientes (Tortoise)
        produto_repo.py          # Repositório de produtos (Tortoise)
        pedido_repo.py           # Repositório de pedidos e itens (Tortoise)
schemas/
    cliente.py                   # Schemas Pydantic de entrada/saída para clientes
    produto.py                   # Schemas Pydantic de entrada/saída para produtos
    pedido.py                    # Schemas Pydantic de entrada/saída para pedidos
services/
    lanchonete_service.py        # Camada de serviço com todas as regras de negócio
tests/
    conftest.py                  # Fixtures: banco em memória + AsyncClient
    test_api_cancelar_pedido.py
    test_api_clientes.py
    test_api_observacao_pedido.py
    test_api_pedidos.py
    test_domain_pedido.py
    test_domain_produto.py
atividades/
    Treino Apis/                 # Enunciados de exercícios práticos por aula
```

---

## Banco de dados

O arquivo `lanchonete.db` (SQLite) é criado automaticamente ao subir a aplicação.  
As tabelas são geradas pelo Tortoise ORM com base nos models definidos em `infrastructure/tortoise/models.py`.

| Tabela          | Descrição                                           |
|-----------------|-----------------------------------------------------|
| `clientemodel`  | Clientes cadastrados (CPF como chave primária)      |
| `produtomodel`  | Produtos disponíveis (código como chave primária)   |
| `pedidomodel`   | Pedidos realizados                                  |
| `pedidoitemmodel` | Itens de cada pedido (relação pedido ↔ produto)   |

---

## Seed — Popular o banco de dados

O script `seed.py` apaga todos os dados existentes e recria um conjunto de
exemplos baseado nos cenários dos testes automatizados.

```bash
python seed.py
```

**Dados inseridos:**

| Tipo | Dados |
|------|-------|
| Clientes | Cliente X (`11122233344`), Joao (`12345678900`), Maria (`99988877766`) |
| Produtos | #1 tipo 1 R\$10 (10% desconto), #2 tipo 2 R\$20, #3 tipo 2 R\$15 |
| Pedido #1 | Finalizado — Cliente X, produtos 1+2, total R\$29,00 |
| Pedido #2 | Cancelado — Joao |
| Pedido #3 | Em aberto com observação "Sem cebola" — Maria |

> O `seed.py` afeta apenas o `lanchonete.db` em disco.  
> Os testes usam banco **em memória** e não são afetados pelo seed.

---

## Utilitários

### Gerar `requirements.txt`

```bash
pip freeze > requirements.txt
```

### Desinstalar todas as bibliotecas

```bash
pip freeze > uninstall.txt
pip uninstall -r uninstall.txt -y
```