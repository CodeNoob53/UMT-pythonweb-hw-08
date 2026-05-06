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

## Known Issues & Fixes

### 1. `ValueError` on February 29 birthday in a non-leap year

**Problem:** `contact.birthday.replace(year=today.year)` raises `ValueError` for contacts born on Feb 29 when the current year is not a leap year. This caused `GET /contacts/birthdays` to return HTTP 500.

**Fix:** Extracted a `_next_birthday()` helper in `app/crud.py` that wraps the `.replace()` call in a `try/except ValueError` and falls back to March 1 — the conventional next-day representation used in most HR and calendar systems.

```python
def _next_birthday(birthday: date, today: date) -> date:
    try:
        candidate = birthday.replace(year=today.year)
    except ValueError:
        candidate = date(today.year, 3, 1)  # Feb 29 → Mar 1 in non-leap years
    ...
```

---

### 2. Duplicate email returns HTTP 500 instead of 409

**Problem:** The `email` column has a `UNIQUE` constraint in the database. Inserting or updating a contact with an already-existing email raised an unhandled `sqlalchemy.exc.IntegrityError`, which FastAPI surfaced as a generic 500 Internal Server Error.

**Fix:** Both `create_contact` and `update_contact` in `app/crud.py` now wrap `db.commit()` in a `try/except IntegrityError` and re-raise. The router catches it and returns a proper `409 Conflict` response.

```python
# crud.py
try:
    db.commit()
except IntegrityError:
    db.rollback()
    raise

# routers/contacts.py
except IntegrityError:
    raise HTTPException(status_code=409, detail="Email already exists")
```

---

### 3. Multi-parameter search used OR instead of AND

**Problem:** The initial implementation combined multiple query parameters with `or_()`, so `?first_name=Ivan&email=test@example.com` returned contacts matching **either** condition — counter-intuitive for a search filter.

**Fix:** Replaced the collected `or_(*filters)` call with sequential `.filter()` chaining, so each provided parameter narrows the result set (AND semantics).

```python
# Before
query = query.filter(or_(*filters))

# After
if first_name:
    query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
if last_name:
    query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
if email:
    query = query.filter(Contact.email.ilike(f"%{email}%"))
```

---

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
