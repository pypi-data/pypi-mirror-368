from fastapi import FastAPI
from src.ycfuncs import FastAPIHandler

app = FastAPI()


@app.get("/")
async def root():
    return 'Hello World!'

handler = FastAPIHandler(app)
