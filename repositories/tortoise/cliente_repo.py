from infrastructure.tortoise.models import ClienteModel
from domain.cliente import Cliente


class ClienteRepoTortoise:
    async def get(self, cpf: str) -> Cliente | None:
        row = await ClienteModel.get_or_none(cpf=cpf)
        if not row:
            return None
        return Cliente(cpf=row.cpf, nome=row.nome)

    async def save(self, cliente: Cliente) -> None:
        await ClienteModel.update_or_create(
            defaults={"nome": cliente.nome},
            cpf=cliente.cpf,
        )
