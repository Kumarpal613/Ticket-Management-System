"""TicketService: business rules. Knows nothing about HTTP or SQL."""
from .models import Ticket
from .repository import TicketRepository
from .schemas import (
    OldestUnresolved,
    Status,
    TicketCreate,
    TicketSummary,
    TicketUpdate,
)


class TicketNotFoundError(Exception):
    def __init__(self, ticket_id: int):
        super().__init__(f"Ticket {ticket_id} not found")
        self.ticket_id = ticket_id


class TicketService:
    def __init__(self, repository: TicketRepository):
        self.repository = repository

    def create(self, data: TicketCreate) -> Ticket:
        return self.repository.add(data.model_dump(mode="json"))

    def list(self, status: Status | None = None) -> list[Ticket]:
        return self.repository.list(status.value if status else None)

    def get(self, ticket_id: int) -> Ticket:
        ticket = self.repository.get(ticket_id)
        if ticket is None:
            raise TicketNotFoundError(ticket_id)
        return ticket

    def update(self, ticket_id: int, data: TicketUpdate) -> Ticket:
        ticket = self.get(ticket_id)
        changes = data.model_dump(mode="json", exclude_none=True)
        return self.repository.update(ticket, changes)

    def delete(self, ticket_id: int) -> None:
        self.repository.delete(self.get(ticket_id))

    def summary(self) -> TicketSummary:
        counts = self.repository.count_by_status()
        oldest = self.repository.oldest_unresolved()
        return TicketSummary(
            total=sum(counts.values()),
            open=counts.get(Status.OPEN.value, 0),
            in_progress=counts.get(Status.IN_PROGRESS.value, 0),
            resolved=counts.get(Status.RESOLVED.value, 0),
            high_priority=self.repository.count_high_priority(),
            oldest_unresolved=(
                OldestUnresolved(id=oldest.id, title=oldest.title) if oldest else None
            ),
        )
