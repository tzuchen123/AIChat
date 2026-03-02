from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_db
from src.middlewares.auth import get_current_user
from src.models.user import User
from src.schemas.common import StandardResponse
from src.schemas.message import MessageCreate, MessageListResponse, MessageResponse
from src.services.message_service import MessageService

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get(
    "/{conversation_id}",
    response_model=StandardResponse[MessageListResponse],
)
async def list_messages(
    conversation_id: int,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MessageService(db)
    result = await service.list_messages(conversation_id, current_user.id, page, limit)
    return StandardResponse.ok(result)


@router.post(
    "/{conversation_id}",
    response_model=StandardResponse[MessageResponse],
    status_code=201,
)
async def send_message(
    conversation_id: int,
    body: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MessageService(db)
    message = await service.send_message(conversation_id, current_user.id, body.content)
    return StandardResponse.ok(message)
