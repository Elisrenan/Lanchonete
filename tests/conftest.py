# =============================================================================
# conftest.py — Configurações compartilhadas entre todos os testes
# =============================================================================
#
# Com a migração para Tortoise ORM async, este arquivo foi reescrito para:
#
#   1. Inicializar o Tortoise com SQLite em memória (:memory:) antes de cada
#      teste, garantindo que cada teste parte de um banco totalmente vazio.
#   2. Fechar a conexão após o teste — o SQLite :memory: é destruído junto,
#      sem deixar nada no disco.
#   3. Fornecer um cliente HTTP assíncrono (httpx.AsyncClient) que despacha
#      requisições direto ao app FastAPI, sem abrir porta de rede.
#
# Por que não usar TestClient (síncrono)?
#   O TestClient cria seu próprio event loop, o que conflita com o Tortoise
#   que já tem uma conexão assíncrona ativa no event loop do pytest-asyncio.
#   O AsyncClient + ASGITransport reutiliza o mesmo event loop, evitando o
#   conflito.
#
# Por que SQLite :memory: e não lanchonete.db?
#   O banco em arquivo acumularia dados entre testes, quebrando o isolamento.
#   Com :memory:, cada conexão começa do zero — sem estado residual.
# =============================================================================

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from tortoise import Tortoise

from main import app

_TORTOISE_TEST_MODULES = {"models": ["infrastructure.tortoise.models"]}


@pytest_asyncio.fixture(autouse=True)
async def init_test_db():
    """Inicializa o banco SQLite em memória e cria as tabelas antes de cada teste.

    Por que isso é necessário?
        O Tortoise ORM precisa de uma conexão ativa para executar qualquer
        operação assíncrona de banco. Em testes, usamos :memory: para garantir
        que cada teste começa com um banco completamente vazio, sem depender
        de estado deixado por testes anteriores.

    O autouse=True faz este fixture rodar automaticamente para TODOS os
    testes, sem precisar declará-lo como parâmetro nas funções de teste.

    Fluxo (separado pelo yield):
        ANTES do teste:
            1. Tortoise.init()       → abre conexão com SQLite :memory:
            2. generate_schemas()    → cria as tabelas (ClienteModel, etc.)
        DEPOIS do teste:
            3. close_connections()   → fecha a conexão, destruindo o :memory:
    """
    await Tortoise.init(db_url="sqlite://:memory:", modules=_TORTOISE_TEST_MODULES)
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest_asyncio.fixture
async def client():
    """Cria um cliente HTTP assíncrono para testar a API sem subir um servidor real.

    O AsyncClient do httpx com ASGITransport despacha as requisições
    diretamente para o app FastAPI no mesmo event loop assíncrono do
    pytest-asyncio. Isso mantém compatibilidade com o Tortoise já
    inicializado pelo fixture init_test_db.

    Como o ASGITransport funciona?
        Ele implementa a interface ASGI, simulando as requisições HTTP
        dentro do processo Python, sem usar sockets de rede reais.
        Isso torna os testes muito mais rápidos.

    Como usar:
        async def test_exemplo(client):        # pytest injeta o client aqui
            r = await client.get("/health")
            assert r.status_code == 200
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

