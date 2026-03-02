from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_db
from src.middlewares.auth import get_current_user
from src.models.user import User
from src.schemas.chat import ConversationCreate, ConversationResponse
from src.schemas.common import StandardResponse
from src.services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/", response_model=StandardResponse[list[ConversationResponse]])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    conversations = await service.list_conversations(current_user.id)
    return StandardResponse.ok(conversations)


@router.post(
    "/",
    response_model=StandardResponse[ConversationResponse],
    status_code=201,
)
async def create_conversation(
    body: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    conversation = await service.create_conversation(current_user.id, body.title)
    return StandardResponse.ok(conversation)


@router.delete("/{conversation_id}", response_model=StandardResponse[None])
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    await service.delete_conversation(conversation_id, current_user.id)
    return StandardResponse.ok(None)
