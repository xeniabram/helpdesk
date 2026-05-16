import asyncio
import json
from collections.abc import AsyncGenerator

from openai import AsyncOpenAI
from sse_starlette.event import ServerSentEvent

from app.core.constants import LLM_SYSTEM_PROMPT, LLM_TTFT_TIMEOUT
from app.models import TicketStatus
from app.repositories.ticket import TicketRepository
from app.schemas import TicketOut


class TicketService:
    def __init__(
        self,
        repo: TicketRepository,
        llm_client: AsyncOpenAI,
        llm_model: str,
    ):
        self._repo = repo
        self._llm_client = llm_client
        self._llm_model = llm_model

    async def list_tickets(self, status: TicketStatus | None = None) -> list[TicketOut]:
        return await self._repo.get_all(status)

    async def get_ticket(self, ticket_id: int) -> TicketOut | None:
        return await self._repo.get_by_id(ticket_id)

    async def generate_summary(self, ticket: TicketOut) -> AsyncGenerator[str | ServerSentEvent]:
        try:
            async with asyncio.timeout(LLM_TTFT_TIMEOUT):
                stream = await self._llm_client.chat.completions.create(
                    model=self._llm_model,
                    messages=[
                        {
                            "role": "system",
                            "content": LLM_SYSTEM_PROMPT,
                        },
                        {
                            "role": "user",
                            "content": f"Title: {ticket.title}\n\nDescription: {ticket.description}",
                        },
                    ],
                    stream=True,
                )
                first_chunk = await anext(aiter(stream))
            if first_chunk.choices and first_chunk.choices[0].delta.content:
                yield json.dumps({"content": first_chunk.choices[0].delta.content})
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield json.dumps({"content": chunk.choices[0].delta.content})
            yield ServerSentEvent(data="", event="done")
        except TimeoutError:
            yield ServerSentEvent(
                data=json.dumps({"error": "LLM took too long to respond"}),
                event="error",
            )
        except Exception as e:
            yield ServerSentEvent(data=json.dumps({"error": str(e)}), event="error")
