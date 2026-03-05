from dataclasses import dataclass
@dataclass
class Produto:
    id: int
    tipo: int
    valor: float
    desconto_percentual: float = 0.0

    def preco_final(self) -> float:
        #Regra: se tipo == 2, Não se aplica desconto
        if self.tipo == 2:
            return self.valor
        if self.desconto_percentual and self.desconto_percentual > 0:
            return self.valor * (1 - self.desconto_percentual / 100)
        return self.valor