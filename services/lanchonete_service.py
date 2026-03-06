from domain.cliente import Cliente
from domain.produto import Produto
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

    def criar_produto(self, id: int, tipo: int, valor: float, desconto_percentual: float = 0.0) -> Produto:
        produto = Produto(id=id, tipo=tipo, valor=valor, desconto_percentual=desconto_percentual)
        db.produtos_por_id[id] = produto
        return produto

    def obter_produto(self):
        pass

    def alterar_valor_produto(self):
        pass

service = LanchoneteService()