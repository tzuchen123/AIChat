from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.chat_repo import ChatRepository
from src.schemas.chat import ConversationResponse


class ChatService:
    def __init__(self, db: AsyncSession):
        self.repo = ChatRepository(db)

    async def list_conversations(self, user_id: int) -> list[ConversationResponse]:
        conversations = await self.repo.get_all_by_user(user_id)
        return [ConversationResponse.model_validate(c) for c in conversations]

    async def create_conversation(
        self, user_id: int, title: Optional[str]
    ) -> ConversationResponse:
        conversation = await self.repo.create(user_id, title)
        return ConversationResponse.model_validate(conversation)

    async def delete_conversation(self, conversation_id: int, user_id: int) -> None:
        conversation = await self.repo.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        await self.repo.delete(conversation_id)

    async def get_conversation(
        self, conversation_id: int, user_id: int
    ) -> ConversationResponse:
        conversation = await self.repo.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        return ConversationResponse.model_validate(conversation)
