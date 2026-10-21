# Support Ticket Management System

A lightweight support-ticket application with a FastAPI and SQLite backend and a React frontend.

## Features

- Create, list, view, update, and delete support tickets
- Filter tickets by status
- Validate ticket titles, statuses, and priorities
- View ticket totals, status counts, high-priority totals, and the oldest unresolved ticket
- Responsive interface with loading and error states

## Technology

- **Backend:** Python 3.10+, FastAPI, SQLAlchemy, SQLite
- **Frontend:** React 18, Vite
- **Tests:** pytest, FastAPI TestClient, in-memory SQLite

## Getting started

### Backend

From the project root, create and activate a virtual environment, install the dependencies, and start the API:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`; interactive API documentation is at `http://localhost:8000/docs`.

The application creates `backend/tickets.db` and its tables on startup. The database file is local and ignored by Git.

### Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite. The frontend uses `http://localhost:8000` by default; set `VITE_API_URL` when the API is hosted at a different address.

## Run tests

```powershell
cd backend
python -m pytest
```

Tests use an in-memory database and do not modify the local ticket database.

## API overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/tickets` | Create a ticket |
| `GET` | `/tickets` | List tickets; optionally filter with `?status=Open` |
| `GET` | `/tickets/summary` | Retrieve ticket summary statistics |
| `GET` | `/tickets/{ticket_id}` | Retrieve a ticket |
| `PATCH` | `/tickets/{ticket_id}` | Update a ticket's status or priority |
| `DELETE` | `/tickets/{ticket_id}` | Delete a ticket |

## Project structure

```text
backend/
  app/          API routes, database, models, validation, and business logic
  tests/        Backend tests
frontend/
  src/          React application and UI components
```

Authentication is not currently implemented. Add appropriate authentication and deployment-specific CORS settings before exposing the API publicly.
