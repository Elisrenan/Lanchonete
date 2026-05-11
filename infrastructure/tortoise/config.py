# =============================================================================
# config.py — Configuração do Tortoise ORM
# =============================================================================
#
# Este módulo expõe o dicionário TORTOISE_ORM que o register_tortoise do
# FastAPI utiliza para saber onde conectar e quais modelos registrar.
#
# connections: URL de conexão com o banco de dados.
#   - Em produção: sqlite://lanchonete.db  (arquivo no disco)
#   - Em testes:   sqlite://:memory:       (banco temporário, destruído ao fechar)
#
# apps/models: caminho Python para o módulo que contém os modelos Tortoise.
#   Tortoise precisa conhecê-los para criar as tabelas (generate_schemas).
# =============================================================================

TORTOISE_ORM = {
    "connections": {"default": "sqlite://lanchonete.db"},
    "apps": {
        "models": {
            "models": ["infrastructure.tortoise.models"],
            "default_connection": "default",
        }
    },
}
