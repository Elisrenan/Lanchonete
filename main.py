#import uvicorn
from fastapi import FastAPI
from api.routes.health import router as health_router
from api.routes.clientes import router as clientes_router
from api.routes.pedidos import router as pedidos_router
from api.routes.produtos import router as produto_router

from fastapi.responses import JSONResponse
from fastapi import Request

from tortoise.contrib.fastapi import register_tortoise
from infrastructure.tortoise.config import TORTOISE_ORM


app = FastAPI(
                title="Projeto Lanchonete",
                description="API para gerenciamento de clientes e produtos da lanchonete",
                version="1.0.0"
            )


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    """Tratamento global de erros do tipo ValueError, retornando status 400."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

app.include_router(health_router)
app.include_router(clientes_router)
app.include_router(produto_router)
app.include_router(pedidos_router)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

#if __name__ == "__main__":
#    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
