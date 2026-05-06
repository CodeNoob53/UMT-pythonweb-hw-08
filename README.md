# Contacts REST API

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?logo=sqlalchemy&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

## About

Homework 8 for the UMT Full-Stack Python Web Development course.

**Goal:** build a production-ready REST API for storing and managing personal contacts.  
The API is built with **FastAPI**, uses **SQLAlchemy ORM** for all database interactions, and **PostgreSQL** as the primary database. Data validation is handled by **Pydantic v2** schemas. The full OpenAPI (Swagger) documentation is generated automatically.

## What Was Done

- Designed a `Contact` database model with all required fields: first name, last name, email, phone, birthday, and optional extra notes
- Implemented full CRUD via REST endpoints (create, read, update, delete)
- Added contact search by `first_name`, `last_name`, or `email` via query parameters (case-insensitive, partial match)
- Added a dedicated endpoint that returns contacts whose birthday falls within the next 7 days
- Configured Pydantic schemas with proper type validation — `birthday` is stored and validated as a `date`, not a plain string
- Documented all endpoints via auto-generated Swagger UI at `/docs`

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL |
| Validation | Pydantic v2 |
| Server | Uvicorn |
| Config | pydantic-settings + python-dotenv |

## Project Structure

```
├── main.py               # App entry point; creates DB tables on startup
├── requirements.txt
├── docker-compose.yml    # PostgreSQL service
├── .env.example          # Environment variable template
└── app/
    ├── config.py         # Settings loaded from .env
    ├── database.py       # SQLAlchemy engine, session factory, Base
    ├── models.py         # Contact ORM model
    ├── schemas.py        # Pydantic schemas: ContactCreate / ContactUpdate / ContactResponse
    ├── crud.py           # All database operations (no raw SQL)
    └── routers/
        └── contacts.py   # REST endpoints
```

## Setup

**1. Clone the repository**

```bash
git clone https://github.com/CodeNoob53/UMT-pythonweb-hw-08.git
cd UMT-pythonweb-hw-08
```

**2. Create a virtual environment and install dependencies**

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**3. Configure environment**

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/contacts_db
```

**4. Start PostgreSQL**

With Docker:

```bash
docker compose up -d
```

Or create the database manually on an existing PostgreSQL instance:

```bash
psql -U postgres -c "CREATE DATABASE contacts_db;"
```

**5. Run the server**

```bash
uvicorn main:app --reload
```

| URL | Description |
|-----|-------------|
| `http://localhost:8000` | API root |
| `http://localhost:8000/docs` | Swagger UI |
| `http://localhost:8000/redoc` | ReDoc |

## API Reference

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/contacts/` | Create a new contact |
| `GET` | `/contacts/` | List all contacts (with optional search) |
| `GET` | `/contacts/birthdays` | Contacts with birthdays in the next 7 days |
| `GET` | `/contacts/{id}` | Get contact by ID |
| `PUT` | `/contacts/{id}` | Update existing contact |
| `DELETE` | `/contacts/{id}` | Delete contact |

### Contact Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `first_name` | `string` | Yes | First name |
| `last_name` | `string` | Yes | Last name |
| `email` | `string` | Yes | Email address (unique) |
| `phone` | `string` | Yes | Phone number |
| `birthday` | `date` | Yes | Date of birth — `YYYY-MM-DD` |
| `extra` | `string` | No | Additional notes |

### Search Parameters

`GET /contacts/` accepts the following optional query parameters:

| Parameter | Description |
|-----------|-------------|
| `first_name` | Partial, case-insensitive match on first name |
| `last_name` | Partial, case-insensitive match on last name |
| `email` | Partial, case-insensitive match on email |

Parameters can be combined. If none are provided, all contacts are returned.

## Usage Examples

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

**Search contacts**

```bash
curl "http://localhost:8000/contacts/?last_name=petrenko"
curl "http://localhost:8000/contacts/?email=example.com"
```

**Get contacts with upcoming birthdays**

```bash
curl http://localhost:8000/contacts/birthdays
```

**Update a contact**

```bash
curl -X PUT http://localhost:8000/contacts/1 \
  -H "Content-Type: application/json" \
  -d '{"phone": "+380991234567"}'
```

**Delete a contact**

```bash
curl -X DELETE http://localhost:8000/contacts/1
```
