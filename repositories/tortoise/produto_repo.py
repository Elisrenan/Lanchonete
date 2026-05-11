# =============================================================================
# produto_repo.py — Repositório de produtos usando Tortoise ORM
# =============================================================================
#
# Implementa as operações de persistência para a entidade Produto.
# Converte entre ProdutoModel (ORM / banco) e Produto (domínio puro).
# =============================================================================

from infrastructure.tortoise.models import ProdutoModel
from domain.produto import Produto


class ProdutoRepoTortoise:
    """Repositório assíncrono de produtos persistidos via Tortoise ORM."""

    async def get(self, codigo: int) -> Produto | None:
        """Busca um produto pelo código.

        Args:
            codigo: Código único do produto.

        Returns:
            Instância de domínio Produto se encontrado, None caso contrário.
        """
        row = await ProdutoModel.get_or_none(codigo=int(codigo))
        if not row:
            return None
        return Produto(
            codigo=row.codigo,
            valor=row.valor,
            tipo=row.tipo,
            desconto_percentual=row.desconto_percentual,
        )

    async def save(self, produto: Produto) -> None:
        """Persiste um produto no banco, criando ou atualizando o registro.

        Os valores são convertidos explicitamente (float, int) para evitar
        problemas de tipo com os campos Tortoise.

        Args:
            produto: Entidade de domínio com os dados a salvar.
        """
        await ProdutoModel.update_or_create(
            defaults={
                "valor": float(produto.valor),
                "tipo": int(produto.tipo),
                "desconto_percentual": float(produto.desconto_percentual),
            },
            codigo=int(produto.codigo),
        )
