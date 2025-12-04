from fastapi import FastAPI, Depends
import uvicorn
from app.authorisation import router as auth_router, security

app = FastAPI()
app.include_router(auth_router)

@app.get("/")
def index():
    return {"message":"Hello Arakis"}

@app.get("/protected", dependencies=[Depends(security.access_token_required)])
def protected():
    return {"data": "TOP SECRET"}

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)