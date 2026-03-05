from domain.cliente import Cliente
from repositories.memory import db

class LanchoneteService:
    def criar_cliente(self, cpf: str, nome: str = "") -> Cliente:
        #regra simples: se já existe, retorna o mesmo
        if cpf in db.clientes_por_cpf:
            return db.clientes_por_cpf[cpf]
        cliente = Cliente(cpf=cpf, nome=nome)
        db.clientes_por_cpf[cpf] = cliente
        return cliente

    def obter_cliente(self, cpf: str) -> Cliente | None:
        return db.clientes_por_cpf.get(cpf)

    def criar_produto(self):
        pass

    def obter_produto(self):
        pass

    def alterar_valor_produto(self):
        pass

service = LanchoneteService()