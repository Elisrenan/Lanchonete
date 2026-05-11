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
