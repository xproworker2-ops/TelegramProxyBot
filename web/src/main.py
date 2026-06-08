from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Імпортуємо наш свіжостворений роутер
from src.admin.router import router as admin_router

load_dotenv()

app = FastAPI(
    title="TG Proxy Bot Admin API",
    description="API для керування тікетами, користувачами та повідомленнями",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "working",
        "message": "Welcome to TG Proxy Bot Admin API",
        "docs": "/docs"
    }

# РЕЄСТРУЄМО НАШ РОУТЕР АДМІНКИ (додаємо префікс для красивої структури URL)
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin Panel"])