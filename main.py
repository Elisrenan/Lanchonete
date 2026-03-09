#import uvicorn
from fastapi import FastAPI
from api.routes.health import router as health_router
from api.routes.clientes import router as clientes_router
from api.routes.produtos import router as produto_router

app = FastAPI(
                title="Projeto Lanchonete", 
                description="API para gerenciamento de clientes e produtos da lanchonete", 
                version="1.0.0"
            )

app.include_router(health_router)
app.include_router(clientes_router)
app.include_router(produto_router)

#if __name__ == "__main__":
#    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
