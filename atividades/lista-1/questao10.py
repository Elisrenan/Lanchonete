"""
Criar funções:
calcular_total(qtd, valor)
calcular_desconto(total) Regras: - Até 100 → sem desconto - Até 300 → 5% - Acima de 300 → 10%
fechar_compra(qtd, valor) Deve exibir:
Total:
Desconto:
Total final:
"""
def calcular_total(qtd: int, valor_unitario: float) -> float:
    if qtd < 0:
        raise ValueError("A quantidade não pode ser negativa.")
    if valor_unitario < 0:
        raise ValueError("O valor unitário não pode ser negativo.")
    
    total = qtd * valor_unitario
    return total

def calcular_desconto(total: float) -> float:
    if total <= 100.0:
        return 0.0
    elif total <= 300.0:
        return total * 0.05
    else:
        return total * 0.10
    
def fechar_compra(qtd: int, valor_unitario: float) -> str:
    total = calcular_total(qtd, valor_unitario)
    desconto = calcular_desconto(total)
    total_final = total - desconto
    return total, desconto, total_final

# Exemplo de uso
quantidade = 10
valor_unitario = 35.0
total, desconto, total_final = fechar_compra(quantidade, valor_unitario)
resultado = f"Total: R$ {total:.2f}\nDesconto: R$ {desconto:.2f}\nTotal final: R$ {total_final:.2f}"
print(resultado)