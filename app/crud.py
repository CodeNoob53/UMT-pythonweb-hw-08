from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import Contact
from app.schemas import ContactCreate, ContactUpdate


def create_contact(db: Session, data: ContactCreate) -> Contact:
    contact = Contact(**data.model_dump())
    db.add(contact)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(contact)
    return contact


def get_contacts(
    db: Session,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
) -> list[Contact]:
    query = db.query(Contact)
    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    return query.all()


def get_contact(db: Session, contact_id: int) -> Optional[Contact]:
    return db.query(Contact).filter(Contact.id == contact_id).first()


def update_contact(db: Session, contact_id: int, data: ContactUpdate) -> Optional[Contact]:
    contact = get_contact(db, contact_id)
    if not contact:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(contact)
    return contact


def delete_contact(db: Session, contact_id: int) -> Optional[Contact]:
    contact = get_contact(db, contact_id)
    if not contact:
        return None
    db.delete(contact)
    db.commit()
    return contact


def _next_birthday(birthday: date, today: date) -> date:
    # Feb 29 in a non-leap year → treat as Mar 1
    try:
        candidate = birthday.replace(year=today.year)
    except ValueError:
        candidate = date(today.year, 3, 1)
    if candidate < today:
        try:
            candidate = birthday.replace(year=today.year + 1)
        except ValueError:
            candidate = date(today.year + 1, 3, 1)
    return candidate


def get_upcoming_birthdays(db: Session) -> list[Contact]:
    today = date.today()
    end = today + timedelta(days=7)
    return [
        c for c in db.query(Contact).all()
        if today <= _next_birthday(c.birthday, today) <= end
    ]
