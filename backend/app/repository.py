from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Ticket
from .schemas import Priority, Status


class TicketRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, values: dict) -> Ticket:
        ticket = Ticket(**values)
        self.session.add(ticket)
        self.session.commit()
        self.session.refresh(ticket)
        return ticket

    def get(self, ticket_id: int) -> Ticket | None:
        return self.session.get(Ticket, ticket_id)

    def list(self, status: str | None = None) -> list[Ticket]:
        query = select(Ticket).order_by(Ticket.created_at.desc(), Ticket.id.desc())
        if status:
            query = query.where(Ticket.status == status)
        return list(self.session.scalars(query))

    def update(self, ticket: Ticket, changes: dict) -> Ticket:
        for field, value in changes.items():
            setattr(ticket, field, value)
        self.session.commit()
        self.session.refresh(ticket)
        return ticket

    def delete(self, ticket: Ticket) -> None:
        self.session.delete(ticket)
        self.session.commit()

    # ---- queries used by the summary ----
    def count_by_status(self) -> dict[str, int]:
        rows = self.session.execute(
            select(Ticket.status, func.count()).group_by(Ticket.status)
        )
        return {status: count for status, count in rows}

    def count_high_priority(self) -> int:
        query = select(func.count()).select_from(Ticket).where(
            Ticket.priority == Priority.HIGH.value
        )
        return self.session.scalar(query) or 0

    def oldest_unresolved(self) -> Ticket | None:
        query = (
            select(Ticket)
            .where(Ticket.status != Status.RESOLVED.value)
            .order_by(Ticket.created_at.asc(), Ticket.id.asc())
            .limit(1)
        )
        return self.session.scalars(query).first()
