# =============================================================================
# deps.py — Fábrica de dependências para injetar via FastAPI Depends()
# =============================================================================
#
# O FastAPI usa o mecanismo de Dependency Injection (DI): em vez de cada
# rota instanciar diretamente o serviço, ela declara o serviço como
# parâmetro e o FastAPI chama a função de fábrica registrada aqui.
#
# Vantagens:
#   - Troca de implementação sem alterar as rotas (ex: memory vs. Tortoise)
#   - Fácil de sobrescrever em testes com app.dependency_overrides
#   - Vida útil do objeto controlada pelo FastAPI (por requisição)
# =============================================================================

from services.lanchonete_service import LanchoneteService
from repositories.tortoise.cliente_repo import ClienteRepoTortoise
from repositories.tortoise.produto_repo import ProdutoRepoTortoise
from repositories.tortoise.pedido_repo import PedidoRepoTortoise


def get_service_tortoise() -> LanchoneteService:
    """Cria e retorna uma instância de LanchoneteService com repositórios Tortoise.

    Esta função é usada como argumento em Depends() nas rotas FastAPI.
    Em cada requisição, o FastAPI a chama e injeta o serviço resultante.

    Returns:
        LanchoneteService configurado com os três repositórios Tortoise ORM.
    """
    return LanchoneteService(
        ClienteRepoTortoise(),
        ProdutoRepoTortoise(),
        PedidoRepoTortoise(),
    )
