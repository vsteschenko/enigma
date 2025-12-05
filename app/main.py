from fastapi import FastAPI, Depends
import uvicorn
from app.routers.authorisation import router as auth_router, security
from app.routers.transactions import router as tx_router
from app.models import Base
from app.db import engine

app = FastAPI()
app.include_router(auth_router)
app.include_router(tx_router)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def index():
    return {"message":"Hello Arakis"}

@app.get("/protected", dependencies=[Depends(security.access_token_required)])
def protected():
    return {"data": "TOP SECRET"}

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)