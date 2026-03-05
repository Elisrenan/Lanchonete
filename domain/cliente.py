from dataclasses import  dataclass

@dataclass(frozen=True)
class Cliente:
    cpf: str
    nome: str = ""