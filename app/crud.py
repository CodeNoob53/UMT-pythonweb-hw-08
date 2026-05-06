from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, extract, and_
from app.models import Contact
from app.schemas import ContactCreate, ContactUpdate


def create_contact(db: Session, data: ContactCreate) -> Contact:
    contact = Contact(**data.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def get_contacts(
    db: Session,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
) -> list[Contact]:
    query = db.query(Contact)
    filters = []
    if first_name:
        filters.append(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        filters.append(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        filters.append(Contact.email.ilike(f"%{email}%"))
    if filters:
        query = query.filter(or_(*filters))
    return query.all()


def get_contact(db: Session, contact_id: int) -> Optional[Contact]:
    return db.query(Contact).filter(Contact.id == contact_id).first()


def update_contact(db: Session, contact_id: int, data: ContactUpdate) -> Optional[Contact]:
    contact = get_contact(db, contact_id)
    if not contact:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(db: Session, contact_id: int) -> Optional[Contact]:
    contact = get_contact(db, contact_id)
    if not contact:
        return None
    db.delete(contact)
    db.commit()
    return contact


def get_upcoming_birthdays(db: Session) -> list[Contact]:
    today = date.today()
    end = today + timedelta(days=7)

    contacts = db.query(Contact).all()
    result = []
    for contact in contacts:
        bday_this_year = contact.birthday.replace(year=today.year)
        if bday_this_year < today:
            bday_this_year = bday_this_year.replace(year=today.year + 1)
        if today <= bday_this_year <= end:
            result.append(contact)
    return result
