from collections.abc import AsyncGenerator

from openai import AsyncOpenAI

from src.config.settings import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class OpenAIService:
    async def stream_response(
        self, messages: list[dict]
    ) -> AsyncGenerator[str, None]:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            stream=True,
        )
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

    def build_context(
        self, history: list, new_user_message: str
    ) -> list[dict]:
        context = [
            {"role": msg.role, "content": msg.content}
            for msg in history[-10:]
        ]
        context.append({"role": "user", "content": new_user_message})
        return context
