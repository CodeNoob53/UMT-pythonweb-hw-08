# Contacts REST API

REST API for storing and managing contacts, built with **FastAPI** and **SQLAlchemy**.  
Supports full CRUD, search by query parameters, and upcoming birthday lookup.

## Tech Stack

- **Python 3.12+**
- **FastAPI** — web framework with automatic OpenAPI docs
- **SQLAlchemy 2.0** — ORM for database interaction
- **PostgreSQL** — primary database
- **Pydantic v2** — request/response validation
- **Alembic** — database migrations
- **Uvicorn** — ASGI server

## Project Structure

```
├── main.py               # App entry point, table creation
├── requirements.txt
├── docker-compose.yml    # PostgreSQL via Docker
├── .env.example
└── app/
    ├── config.py         # Settings via pydantic-settings
    ├── database.py       # Engine, session, Base
    ├── models.py         # Contact ORM model
    ├── schemas.py        # Pydantic schemas (Create / Update / Response)
    ├── crud.py           # Database operations
    └── routers/
        └── contacts.py   # API endpoints
```

## Setup

**1. Clone and install dependencies**

```bash
git clone https://github.com/your-username/UMT-pythonweb-hw-08.git
cd UMT-pythonweb-hw-08
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2. Configure environment**

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/contacts_db
```

**3. Start PostgreSQL**

```bash
docker compose up -d
```

Or use a local PostgreSQL instance and create the database manually:

```bash
psql -U postgres -c "CREATE DATABASE contacts_db;"
```

**4. Run the server**

```bash
uvicorn main:app --reload
```

The app will be available at `http://localhost:8000`.  
Interactive API docs: `http://localhost:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/contacts/` | Create a new contact |
| `GET` | `/contacts/` | List all contacts (supports search) |
| `GET` | `/contacts/{id}` | Get contact by ID |
| `PUT` | `/contacts/{id}` | Update contact |
| `DELETE` | `/contacts/{id}` | Delete contact |
| `GET` | `/contacts/birthdays` | Contacts with birthdays in the next 7 days |

## Search

The `GET /contacts/` endpoint supports optional query parameters for filtering:

| Parameter | Description |
|-----------|-------------|
| `first_name` | Filter by first name (case-insensitive, partial match) |
| `last_name` | Filter by last name (case-insensitive, partial match) |
| `email` | Filter by email (case-insensitive, partial match) |

**Example:**

```
GET /contacts/?first_name=ivan&email=example.com
```

## Contact Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `first_name` | `string` | Yes | First name |
| `last_name` | `string` | Yes | Last name |
| `email` | `string` | Yes | Email address (unique) |
| `phone` | `string` | Yes | Phone number |
| `birthday` | `date` | Yes | Date of birth (`YYYY-MM-DD`) |
| `extra` | `string` | No | Additional notes |

## Example Requests

**Create a contact**

```bash
curl -X POST http://localhost:8000/contacts/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Ivan",
    "last_name": "Petrenko",
    "email": "ivan@example.com",
    "phone": "+380501234567",
    "birthday": "1990-05-10",
    "extra": "Friend"
  }'
```

**Search by last name**

```bash
curl "http://localhost:8000/contacts/?last_name=petrenko"
```

**Get upcoming birthdays**

```bash
curl http://localhost:8000/contacts/birthdays
```

**Update phone number**

```bash
curl -X PUT http://localhost:8000/contacts/1 \
  -H "Content-Type: application/json" \
  -d '{"phone": "+380991234567"}'
```

**Delete a contact**

```bash
curl -X DELETE http://localhost:8000/contacts/1
```
