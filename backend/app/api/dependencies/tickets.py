from typing import Annotated

from fastapi import Depends
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_session
from app.core.config import settings
from app.repositories.ticket import TicketRepository
from app.services.ticket import TicketService

SessionDep = Annotated[AsyncSession, Depends(get_session)]

_llm_client = AsyncOpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)


def get_ticket_repository(session: SessionDep) -> TicketRepository:
    return TicketRepository(session)


TicketRepoDep = Annotated[TicketRepository, Depends(get_ticket_repository)]


def get_ticket_service(repo: TicketRepoDep) -> TicketService:
    return TicketService(repo, _llm_client, settings.llm_model)


TicketServiceDep = Annotated[TicketService, Depends(get_ticket_service)]
