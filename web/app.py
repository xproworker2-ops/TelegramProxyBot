from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="TG Proxy Bot Web")

@app.get("/")
async def read_root():
    return {"service": "tg-proxy-bot web", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
