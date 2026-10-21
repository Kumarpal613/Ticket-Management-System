import os
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tickets.db")


class Base(DeclarativeBase):
    """Parent class of every ORM model."""


class Database:
    def __init__(self, url: str):
        options = {}
        if url.startswith("sqlite"):
            # FastAPI may use a session from a different thread than the one that made it.
            options["connect_args"] = {"check_same_thread": False}
            if ":memory:" in url:
                # Keep ONE connection so the in-memory DB survives between requests (tests).
                options["poolclass"] = StaticPool
        self.engine = create_engine(url, **options)
        self._session_factory = sessionmaker(
            bind=self.engine, autoflush=False, expire_on_commit=False
        )

    def create_tables(self) -> None:
        from . import models  # noqa: F401  (import registers the Ticket table on Base)

        Base.metadata.create_all(self.engine)

    def get_session(self) -> Iterator[Session]:
        """Yield a session for one request, always close it afterwards."""
        session = self._session_factory()
        try:
            yield session
        finally:
            session.close()


database = Database(DATABASE_URL)
