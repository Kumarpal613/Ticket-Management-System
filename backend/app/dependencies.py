from typing import Iterator

from fastapi import Depends
from sqlalchemy.orm import Session

from .database import database
from .repository import TicketRepository
from .service import TicketService


def get_session() -> Iterator[Session]:
    yield from database.get_session()


def get_service(session: Session = Depends(get_session)) -> TicketService:
    return TicketService(TicketRepository(session))
