from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Ticket, TicketStatus
from app.schemas import TicketOut


class TicketRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self, status: TicketStatus | None = None) -> list[TicketOut]:
        query = select(Ticket)
        if status:
            query = query.where(Ticket.status == status)
        query = query.order_by(Ticket.created_at.desc())
        result = await self._session.execute(query)
        return [TicketOut.model_validate(t) for t in result.scalars().all()]

    async def get_by_id(self, ticket_id: int) -> TicketOut | None:
        result = await self._session.execute(select(Ticket).where(Ticket.id == ticket_id))
        ticket = result.scalar_one_or_none()
        if not ticket:
            return None
        return TicketOut.model_validate(ticket)
