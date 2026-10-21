from fastapi import APIRouter, Depends, Response, status

from .dependencies import get_service
from .schemas import Status, TicketCreate, TicketOut, TicketSummary, TicketUpdate
from .service import TicketService


class TicketRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/tickets", tags=["tickets"])
        # /summary MUST be registered before /{ticket_id}, otherwise FastAPI would try
        # to read the word "summary" as a ticket id and return 422.
        self.router.add_api_route("/summary", self.get_summary, methods=["GET"],
                                  response_model=TicketSummary)
        self.router.add_api_route("", self.create_ticket, methods=["POST"],
                                  response_model=TicketOut,
                                  status_code=status.HTTP_201_CREATED)
        self.router.add_api_route("", self.list_tickets, methods=["GET"],
                                  response_model=list[TicketOut])
        self.router.add_api_route("/{ticket_id}", self.get_ticket, methods=["GET"],
                                  response_model=TicketOut)
        self.router.add_api_route("/{ticket_id}", self.update_ticket, methods=["PATCH"],
                                  response_model=TicketOut)
        self.router.add_api_route("/{ticket_id}", self.delete_ticket, methods=["DELETE"],
                                  status_code=status.HTTP_204_NO_CONTENT)

    def get_summary(self, service: TicketService = Depends(get_service)):
        return service.summary()

    def create_ticket(self, data: TicketCreate, service: TicketService = Depends(get_service)):
        return service.create(data)

    def list_tickets(self, status: Status | None = None,
                     service: TicketService = Depends(get_service)):
        return service.list(status)

    def get_ticket(self, ticket_id: int, service: TicketService = Depends(get_service)):
        return service.get(ticket_id)

    def update_ticket(self, ticket_id: int, data: TicketUpdate,
                      service: TicketService = Depends(get_service)):
        return service.update(ticket_id, data)

    def delete_ticket(self, ticket_id: int, service: TicketService = Depends(get_service)):
        service.delete(ticket_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
