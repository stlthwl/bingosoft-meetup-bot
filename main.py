from fastapi import FastAPI, HTTPException
from bot import start_bot

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    try:
        await start_bot()  # Измените на асинхронный вызов
    except Exception as e:
        print(e)


@app.get("/")
async def read_root():
    return {"code": 200, "message": "server is running"}

