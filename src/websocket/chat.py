import json
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import AsyncSessionLocal
from src.config.settings import settings
from src.repositories.chat_repo import ChatRepository
from src.repositories.message_repo import MessageRepository
from src.repositories.user_repo import UserRepository
from src.services.openai_service import OpenAIService

router = APIRouter()


async def _authenticate(token: str, db: AsyncSession) -> Optional[int]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        return None

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    return user.id if user else None


@router.websocket("/ws/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: int):
    token = websocket.query_params.get("token", "")
    await websocket.accept()

    async with AsyncSessionLocal() as db:
        user_id = await _authenticate(token, db)
        if not user_id:
            await websocket.send_text(
                json.dumps({"type": "error", "detail": "Unauthorized"})
            )
            await websocket.close(code=1008)
            return

        chat_repo = ChatRepository(db)
        conversation = await chat_repo.get_by_id(conversation_id)
        if not conversation or conversation.user_id != user_id:
            await websocket.send_text(
                json.dumps({"type": "error", "detail": "Conversation not found"})
            )
            await websocket.close(code=1008)
            return

        message_repo = MessageRepository(db)
        openai_service = OpenAIService()

        try:
            while True:
                data = await websocket.receive_text()
                payload = json.loads(data)
                user_content = payload.get("content", "").strip()
                if not user_content:
                    continue

                await message_repo.create(conversation_id, "user", user_content)

                history = await message_repo.get_recent(conversation_id, limit=10)
                messages_context = openai_service.build_context(history[:-1], user_content)

                full_response = ""
                async for chunk in openai_service.stream_response(messages_context):
                    full_response += chunk
                    await websocket.send_text(
                        json.dumps({"type": "stream_chunk", "content": chunk})
                    )

                ai_message = await message_repo.create(
                    conversation_id, "assistant", full_response
                )
                await websocket.send_text(
                    json.dumps({"type": "stream_end", "message_id": ai_message.id})
                )

        except WebSocketDisconnect:
            pass
        except Exception as e:
            try:
                await websocket.send_text(
                    json.dumps({"type": "error", "detail": str(e)})
                )
            except Exception:
                pass
        finally:
            pass
