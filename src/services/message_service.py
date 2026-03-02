from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.chat_repo import ChatRepository
from src.repositories.message_repo import MessageRepository
from src.schemas.message import MessageListResponse, MessageResponse
from src.services.openai_service import OpenAIService


class MessageService:
    def __init__(self, db: AsyncSession):
        self.repo = MessageRepository(db)
        self.chat_repo = ChatRepository(db)
        self.openai = OpenAIService()

    async def _verify_access(self, conversation_id: int, user_id: int) -> None:
        conversation = await self.chat_repo.get_by_id(conversation_id)
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

    async def list_messages(
        self, conversation_id: int, user_id: int, page: int, limit: int
    ) -> MessageListResponse:
        limit = min(limit, 100)
        await self._verify_access(conversation_id, user_id)
        messages, total = await self.repo.get_paginated(conversation_id, page, limit)
        return MessageListResponse(
            messages=[MessageResponse.model_validate(m) for m in messages],
            total=total,
            page=page,
            limit=limit,
        )

    async def send_message(
        self, conversation_id: int, user_id: int, content: str
    ) -> MessageResponse:
        await self._verify_access(conversation_id, user_id)

        await self.repo.create(conversation_id, "user", content)

        history = await self.repo.get_recent(conversation_id, limit=10)
        messages_context = self.openai.build_context(history[:-1], content)

        full_response = ""
        async for chunk in self.openai.stream_response(messages_context):
            full_response += chunk

        ai_message = await self.repo.create(conversation_id, "assistant", full_response)
        return MessageResponse.model_validate(ai_message)
