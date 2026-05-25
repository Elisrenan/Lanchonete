````md
# PROJETO FINAL — API LANCHONETE

## Disciplina

Desenvolvimento de APIs com Python e FastAPI

---

# Objetivo da Atividade

Desenvolver uma evolução completa da API da Lanchonete aplicando todos os conceitos estudados durante o semestre.

O projeto deverá seguir o padrão arquitetural utilizado nas aulas e no repositório base:
https://github.com/Elisrenan/Lanchonete
---

# Tempo de Desenvolvimento

```text
3 horas
```

---

# Cenário

A lanchonete agora precisa de um sistema mais completo para controle operacional dos pedidos.

A equipe deseja:

- Organizar a fila de preparo
- Permitir cancelamentos
- Permitir observações no pedido
- Priorizar determinados pedidos
- Melhorar o fluxo interno da cozinha

Seu objetivo será implementar todas essas funcionalidades na API.

---

# Regras Gerais do Sistema

Todo pedido deverá possuir:

- Cliente
- Lista de produtos
- Status de entrega
- Status de cancelamento
- Prioridade
- Observação opcional

---

# Funcionalidades Obrigatórias

---

# 1. Cancelamento de Pedido

Um pedido poderá ser cancelado apenas se:

- Ainda não estiver entregue

Regras:

- Pedidos cancelados não aparecem na fila de preparo
- Um pedido já cancelado não pode ser cancelado novamente

---

# 2. Observação do Pedido

O cliente poderá adicionar observações no pedido.

Exemplos:

- Sem cebola
- Sem molho
- Carne ao ponto
- Tirar ketchup

Regras:

- Máximo 200 caracteres
- Não permitir texto vazio
- Não permitir observação em pedido entregue

---

# 3. Prioridade de Pedido

O sistema deverá permitir marcar um pedido como prioritário.

Regras:

- Apenas pedidos ativos podem virar prioritários
- Pedidos prioritários devem aparecer primeiro na fila

---

# 4. Fila de Preparo

A fila da cozinha deverá:

- Mostrar pedidos prioritários primeiro
- Depois mostrar pedidos normais
- Não listar pedidos cancelados
- Não listar pedidos entregues

---

# Estrutura Obrigatória do Projeto

O projeto deve seguir o padrão arquitetural utilizado durante o semestre.

```text
domain/
schemas/
repositories/
services/
api/routes/
tests/
```

---

# Parte 1 — Domain

Arquivo esperado:

```text
domain/pedido.py
```

---

## Atributos obrigatórios

Adicionar na classe Pedido:

```python
self.esta_cancelado = False
self.prioritario = False
self.observacao = ""
```

---

## Métodos obrigatórios

Implementar:

```python
def cancelar(self) -> bool:
    pass
```

```python
def adicionar_observacao(
    self,
    observacao: str
) -> bool:
    pass
```

```python
def tornar_prioritario(self) -> bool:
    pass
```

---

# Parte 2 — Schemas

Arquivo esperado:

```text
schemas/pedido.py
```

---

## Schema de entrada

```python
class ObservacaoInput(BaseModel):
    observacao: str
```

---

## Schema de saída

```python
class PedidoFilaOut(BaseModel):
    codigo: int
    cpf: str
    prioritario: bool
    observacao: str
```

---

# Parte 3 — Services

Arquivo esperado:

```text
services/lanchonete_service.py
```

---

## Métodos obrigatórios

Implementar:

```python
def cancelar_pedido(
    self,
    cod_pedido: int
):
    pass
```

---

```python
def adicionar_observacao(
    self,
    cod_pedido: int,
    observacao: str
):
    pass
```

---

```python
def tornar_pedido_prioritario(
    self,
    cod_pedido: int
):
    pass
```

---

```python
def listar_fila_preparo(self):
    pass
```

---

# Parte 4 — API

Arquivo esperado:

```text
api/routes/pedidos.py
```

---

# Endpoint 1 — Adicionar observação

```http
POST /lanchonete/pedidos/{cod_pedido}/observacao
```

### Payload esperado

```json
{
  "observacao": "Sem cebola"
}
```

---

# Endpoint 2 — Cancelar pedido

```http
POST /lanchonete/pedidos/{cod_pedido}/cancelar
```

---

# Endpoint 3 — Tornar pedido prioritário

```http
POST /lanchonete/pedidos/{cod_pedido}/prioridade
```

---

# Endpoint 4 — Listar fila de preparo

```http
GET /lanchonete/pedidos/fila/preparo
```

---

# Regras da API

A API deve:

- Utilizar FastAPI
- Utilizar HTTPException
- Retornar status corretos
- Utilizar response_model quando necessário
- Validar erros corretamente
- Seguir o padrão do projeto

---

# Parte 5 — Testes Automatizados

Os testes devem ser implementados utilizando:

```text
Pytest
```

---

# Estrutura esperada

```text
tests/
```

---

# Testes Obrigatórios

Implementar os seguintes testes:

```python
def test_deve_cancelar_pedido():
    pass
```

---

```python
def test_nao_deve_cancelar_pedido_entregue():
    pass
```

---

```python
def test_deve_adicionar_observacao():
    pass
```

---

```python
def test_nao_deve_aceitar_observacao_vazia():
    pass
```

---

```python
def test_deve_tornar_pedido_prioritario():
    pass
```

---

```python
def test_fila_deve_ter_prioritarios_primeiro():
    pass
```

---

```python
def test_fila_nao_deve_listar_cancelados():
    pass
```

---

# Requisitos Técnicos Obrigatórios

- Utilizar orientação a objetos
- Utilizar tipagem
- Não colocar regra de negócio nas rotas
- Seguir arquitetura em camadas
- Utilizar FastAPI corretamente
- Utilizar Pytest corretamente

---

# Execução dos Testes

```bash
pytest -q
```

---

# Entrega Esperada

```text
domain/
schemas/
services/
api/routes/
tests/
```
