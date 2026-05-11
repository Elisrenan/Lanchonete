TORTOISE_ORM = {
    "connections": {"default": "sqlite://lanchonete.db"},
    "apps": {
        "models": {
            "models": ["infrastructure.tortoise.models"],
            "default_connection": "default",
        }
    },
}
