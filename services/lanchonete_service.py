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

    def criar_produto(self, codigo: int, valor: float, tipo: int, desconto_percentual: float = 0.0) -> Produto:
        produto = Produto(codigo=codigo, valor=valor, tipo=tipo, desconto_percentual=desconto_percentual)
        db.produtos_por_codigo[codigo] = produto
        return produto

    def obter_produto(self, codigo: int) -> Produto | None:
        return db.produtos_por_codigo.get(codigo)

    def alterar_valor_produto(self, codigo: int, novo_valor: float) -> bool:
        produto = self.obter_produto(codigo)
        if not produto:
            return False
        produto.valor = novo_valor
        return True

service = LanchoneteService()