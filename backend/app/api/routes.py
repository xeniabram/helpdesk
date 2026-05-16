from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.api.dependencies.tickets import TicketServiceDep
from app.models import TicketStatus
from app.schemas import TicketOut

router = APIRouter(prefix="/api")


@router.get("/tickets", response_model=list[TicketOut])
async def list_tickets(
    service: TicketServiceDep,
    status: TicketStatus | None = None,
):
    return await service.list_tickets(status)


@router.get("/tickets/{ticket_id}", response_model=TicketOut)
async def get_ticket(
    ticket_id: int,
    service: TicketServiceDep,
):
    ticket = await service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("/tickets/{ticket_id}/summary")
async def get_ticket_summary(
    ticket_id: int,
    service: TicketServiceDep,
):
    ticket = await service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return EventSourceResponse(service.generate_summary(ticket))
