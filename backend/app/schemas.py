from datetime import datetime

from pydantic import BaseModel

from app.models import TicketStatus


class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    status: TicketStatus
    created_at: datetime

    model_config = {"from_attributes": True}
