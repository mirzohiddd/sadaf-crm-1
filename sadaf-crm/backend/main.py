from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app import seed
from app.config import CORS_ORIGINS, ai_enabled
from app.routers import (
    ai,
    attendance,
    auth,
    crud,
    employees,
    insights,
    integrations,
    leads,
    notifications,
    reports,
    settings,
    tasks,
)
from app.security import decode_token
from app.services.realtime import manager as realtime_manager
@asynccontextmanager
async def lifespan(_: FastAPI):
    seed.run()
    realtime_manager.bind_loop(asyncio.get_running_loop())
    print(f"[sadaf] AI: {'anthropic' if ai_enabled() else 'offline (rule-based)'}")
    print("[sadaf] Real vaqtli sinxronizatsiya (WebSocket): yoqilgan")
    yield


app = FastAPI(
    title="SADAF CRM API",
    version="1.0.0",
    description="Turagentlik CRM backendi. Barcha ma'lumot JSON fayllarda saqlanadi.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    # Development qulayligi: localhost/127.0.0.1 dagi ISTALGAN port
    # (frontend, landing va h.k.) har doim ruxsat etiladi — shuning uchun
    # landing yoki frontend portini o'zgartirsangiz ham CORS xatosi
    # chiqmaydi. Productionda haqiqiy domenlar CORS_ORIGINS orqali
    # (.env dagi) alohida ruxsat etiladi.
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)
for router in (
    auth.router,
    employees.router,
    leads.router,
    crud.clients_router,
    crud.tours_router,
    crud.sales_router,
    tasks.router,
    notifications.router,
    attendance.router,
    insights.dashboard_router,
    insights.analytics_router,
    insights.activity_router,
    reports.router,
    settings.router,
    ai.router,
    integrations.router,
):
    app.include_router(router)


@app.get("/api/health", tags=["system"])
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "ai": "anthropic" if ai_enabled() else "local",
    }


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket, token: str = "") -> None:
    """Real vaqtli yangilanishlar kanali.

    Frontend login qilgach shu kanalga ulanadi. Har safar biror hodim
    biror ma'lumotni (masalan vazifa) o'zgartirsa — barcha ulangan
    mijozlarga zudlik bilan signal boradi va ular tegishli bo'limni
    qayta yuklaydi.
    """
    payload = decode_token(token) if token else None
    if not payload:
        await websocket.close(code=4401)
        return

    user_id = int(payload.get("sub", 0)) or None
    await realtime_manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        realtime_manager.disconnect(websocket)
    except Exception:  # noqa: BLE001
        realtime_manager.disconnect(websocket)


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception) -> JSONResponse:
    """Kutilmagan xato butun CRM ni yiqitmasin."""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Serverda kutilmagan xato: {exc}"},
    )