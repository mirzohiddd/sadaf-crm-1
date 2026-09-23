"""Konfiguratsiya — barcha sozlamalar .env orqali beriladi."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = Path(os.getenv("DATA_DIR") or (BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

EXPORT_DIR = DATA_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# ——— Auth ———
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))

ADMIN_LOGIN = os.getenv("ADMIN_LOGIN", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_NAME = os.getenv("ADMIN_NAME", "Super Admin")

# ——— CORS ———
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if o.strip()
]

# ——— AI ———
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6").strip()
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com").strip()
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "1200"))

def ai_enabled() -> bool:
    """Tashqi AI ulangan-ulanmaganini bildiradi."""
    return bool(ANTHROPIC_API_KEY)


# ——— Google Sheets → CRM lead integratsiyasi ———
# Google Sheetsdagi Apps Script shu "maxfiy kalit"ni har bir so'rovda
# yuborishi kerak (header: X-Sheets-Secret). Productionda albatta
# o'zgartiring — aks holda istalgan kishi soxta lead yubora oladi.
SHEETS_WEBHOOK_SECRET = os.getenv("SHEETS_WEBHOOK_SECRET", "dev-sheets-secret-change-me")
# Sheetdan `source` maydoni kelmasa shu qiymat ishlatiladi.
SHEETS_DEFAULT_SOURCE = os.getenv("SHEETS_DEFAULT_SOURCE", "Google Sheets")


# ——— Lead Form (sadaf-landing) → CRM lead integratsiyasi ———
# Landing sahifadagi ariza formasi shu "maxfiy kalit"ni har bir so'rovda
# yuborishi kerak (header: X-Website-Secret). Bu, kim CRM'ga soxta lead
# yubormasligi uchun eng oddiy himoya — chunki forma login qilmagan
# tashrifchi tomonidan to'ldiriladi va JWT talab qilib bo'lmaydi.
# Productionda albatta o'zgartiring va buni frontenddagi
# VITE_LEAD_API_KEY bilan bir xil qiymatga sozlang.
WEBSITE_WEBHOOK_SECRET = os.getenv("WEBSITE_WEBHOOK_SECRET", "dev-website-secret-change-me")
# Lead Form'dan `source` maydoni kelmasa shu qiymat ishlatiladi.
WEBSITE_DEFAULT_SOURCE = os.getenv("WEBSITE_DEFAULT_SOURCE", "Veb-sayt")