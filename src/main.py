from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.middlewares.cors import setup_cors
from src.routers import auth, chat, message
from src.websocket import chat as ws_chat

app = FastAPI(title="AI Chat Platform", version="1.0.0")

setup_cors(app)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(message.router)
app.include_router(ws_chat.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(exc)},
        },
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
