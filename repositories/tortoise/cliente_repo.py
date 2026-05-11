# =============================================================================
# cliente_repo.py — Repositório de clientes usando Tortoise ORM
# =============================================================================
#
# Implementa as operações de persistência para a entidade Cliente.
# Converte entre ClienteModel (ORM / banco) e Cliente (domínio puro).
#
# Padrão Repository: a camada de serviço nunca conhece o banco diretamente;
# ela só chama métodos como get() e save() sem saber como os dados são
# armazenados. Isso facilita trocar o banco sem mudar as regras de negócio.
# =============================================================================

from infrastructure.tortoise.models import ClienteModel
from domain.cliente import Cliente


class ClienteRepoTortoise:
    """Repositório assíncrono de clientes persistidos via Tortoise ORM."""

    async def get(self, cpf: str) -> Cliente | None:
        """Busca um cliente pelo CPF.

        Args:
            cpf: CPF a ser pesquisado (deve corresponder exatamente ao valor salvo).

        Returns:
            Instância de domínio Cliente se encontrado, None caso contrário.
        """
        row = await ClienteModel.get_or_none(cpf=cpf)
        if not row:
            return None
        return Cliente(cpf=row.cpf, nome=row.nome)

    async def save(self, cliente: Cliente) -> None:
        """Persiste um cliente no banco, criando ou atualizando o registro.

        Usa update_or_create: se o CPF já existir, atualiza o nome;
        se não existir, cria um novo registro.

        Args:
            cliente: Entidade de domínio com os dados a salvar.
        """
        await ClienteModel.update_or_create(
            defaults={"nome": cliente.nome},
            cpf=cliente.cpf,
        )
