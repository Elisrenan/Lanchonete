"""
Criar uma função:
mostrar_tabuada(numero)
A função deve exibir a tabuada de 1 até 10.
"""
def mostrar_tabuada(numero):
    print(f"Tabuada do {numero}:")
    for i in range(1, 11):
        resultado = numero * i
        print(f"{numero} x {i} = {resultado}")

# Exemplo de uso
numero = 5
mostrar_tabuada(numero)
