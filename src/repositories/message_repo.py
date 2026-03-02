from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.message import Message


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_paginated(
        self, conversation_id: int, page: int, limit: int
    ) -> tuple[list[Message], int]:
        offset = (page - 1) * limit

        count_result = await self.db.execute(
            select(func.count()).where(Message.conversation_id == conversation_id)
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def get_recent(self, conversation_id: int, limit: int = 10) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        return list(reversed(messages))

    async def create(self, conversation_id: int, role: str, content: str) -> Message:
        message = Message(conversation_id=conversation_id, role=role, content=content)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
