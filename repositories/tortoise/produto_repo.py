from infrastructure.tortoise.models import ProdutoModel
from domain.produto import Produto


class ProdutoRepoTortoise:
    async def get(self, codigo: int) -> Produto | None:
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
        await ProdutoModel.update_or_create(
            defaults={
                "valor": float(produto.valor),
                "tipo": int(produto.tipo),
                "desconto_percentual": float(produto.desconto_percentual),
            },
            codigo=int(produto.codigo),
        )
