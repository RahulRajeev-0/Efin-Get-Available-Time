# app/crud.py
from sqlalchemy.orm import Session
from app.models import User, GeneralAvailability
from app.schemas import UserCreate, GeneralAvailabilityCreate
from fastapi import HTTPException
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

def create_user(db: Session, user: UserCreate):
    db_user = User(name=user.name, email=user.email, time_zone=user.time_zone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_general_availability(db: Session, availability: GeneralAvailabilityCreate):
    try:
        # Check if the availability already exists for the user on the given day and time
        existing_availability = db.query(GeneralAvailability).filter(
            GeneralAvailability.user_id == availability.user_id,
            GeneralAvailability.day == availability.day,
            GeneralAvailability.time_zone == availability.time_zone
        ).all()

        # Check for overlapping time slots
        for existing in existing_availability:
            if (
                (availability.start_time >= existing.start_time and availability.start_time < existing.end_time) or
                (availability.end_time > existing.start_time and availability.end_time <= existing.end_time) or
                (availability.start_time <= existing.start_time and availability.end_time >= existing.end_time)
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"Time slot {availability.start_time} - {availability.end_time} overlaps with an existing availability for user {availability.user_id}."
                )

        # Create the general availability record if no overlap
        db_availability = GeneralAvailability(
            user_id=availability.user_id,
            day=availability.day,
            start_time=availability.start_time,
            end_time=availability.end_time,
            time_zone=availability.time_zone,
        )
        db.add(db_availability)
        db.commit()
        db.refresh(db_availability)
        return db_availability

    except IntegrityError as e:
        db.rollback()
        logging.error(f"IntegrityError: {str(e)}")
        raise HTTPException(status_code=400, detail="Database constraint violation error.")
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"SQLAlchemyError: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected database error occurred.")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")