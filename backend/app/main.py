from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .database import database
from .routes import TicketRouter
from .service import TicketNotFoundError


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.create_tables()  # creates tickets.db on first start
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Support Ticket Management System", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(TicketNotFoundError)
    async def handle_not_found(request: Request, exc: TicketNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    app.include_router(TicketRouter().router)
    return app


app = create_app()
