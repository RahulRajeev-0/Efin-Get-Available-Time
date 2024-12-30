# app/crud.py
from sqlalchemy.orm import Session
from app.models import User, GeneralAvailability, CustomAvailability, Schedule
from app.schemas import UserCreate, GeneralAvailabilityCreate, CustomAvailabilityCreate
from fastapi import HTTPException
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pytz import timezone
import pytz
from datetime import datetime, date, timedelta
from typing import List


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
    

def create_custom_availability(db: Session, availability: CustomAvailabilityCreate):
    try:
        # Check if the custom availability already exists for the user on the given date and time
        existing_availability = db.query(CustomAvailability).filter(
            CustomAvailability.user_id == availability.user_id,
            CustomAvailability.date == availability.date,
            CustomAvailability.time_zone == availability.time_zone
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
                    detail=f"Time slot {availability.start_time} - {availability.end_time} on {availability.date} overlaps with an existing custom availability for user {availability.user_id}."
                )

        # Create the custom availability record if no overlap
        db_availability = CustomAvailability(
            user_id=availability.user_id,
            date=availability.date,
            start_time=availability.start_time,
            end_time=availability.end_time,
            time_zone=availability.time_zone,
        )
        db.add(db_availability)
        db.commit()
        db.refresh(db_availability)
        return db_availability

    except HTTPException as e :
        raise HTTPException(
                    status_code=400,
                    detail=f"Time slot {availability.start_time} - {availability.end_time} on {availability.date} overlaps with an existing custom availability for user {availability.user_id}."
                )

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    


from datetime import datetime, timedelta
from typing import List, Dict
from pytz import timezone

def get_common_availability(db: Session, user_ids: List[int], start_date: date, end_date: date, tz: str) -> Dict:
    # Convert timezone
    user_timezone = timezone(tz)

    # Store availability per user
    user_availability = []

    # Iterate over all user IDs
    for user_id in user_ids:
        # Fetch custom and general availability
        custom_availability = db.query(CustomAvailability).filter(
            CustomAvailability.user_id == user_id,
            CustomAvailability.date.between(start_date, end_date)
        ).all()

        general_availability = db.query(GeneralAvailability).filter(
            GeneralAvailability.user_id == user_id
        ).all()

        # Fetch scheduled events
        scheduled_events = db.query(Schedule).filter(
            Schedule.user_id == user_id,
            Schedule.date.between(start_date, end_date)
        ).all()

        # If no availability at all, this user cannot contribute to common availability
        if not custom_availability and not general_availability:
            return {}  # No common availability possible

        # Track availability for this user
        user_slots = {}

        # Handle custom availability
        for availability in custom_availability:
            date_str = availability.date.strftime('%d-%m-%Y')
            start_time = availability.start_time
            end_time = availability.end_time

            # Convert to localized time
            start_time = user_timezone.localize(datetime.combine(availability.date, start_time))
            end_time = user_timezone.localize(datetime.combine(availability.date, end_time))

            # Check for conflicts with events
            conflicts = False
            for event in scheduled_events:
                event_start = event.start_time
                event_end = event.end_time

                if start_time < event_end and end_time > event_start:  # Overlapping event
                    conflicts = True
                    break

            # If no conflict, add to slots
            if not conflicts:
                user_slots.setdefault(date_str, [])
                user_slots[date_str].append(f"{start_time.strftime('%I:%M%p')}-{end_time.strftime('%I:%M%p')}")

        # Handle general availability if no custom slots exist for a date
        for availability in general_availability:
            current_date = start_date
            while current_date <= end_date:
                if availability.day.lower() == current_date.strftime('%A').lower():  # Match weekday
                    date_str = current_date.strftime('%d-%m-%Y')
                    start_time = availability.start_time
                    end_time = availability.end_time

                    # Convert to localized time
                    start_time = user_timezone.localize(datetime.combine(current_date, start_time))
                    end_time = user_timezone.localize(datetime.combine(current_date, end_time))

                    # Check for conflicts
                    conflicts = False
                    for event in scheduled_events:
                        event_start = event.start_time
                        event_end = event.end_time

                        if start_time < event_end and end_time > event_start:  # Overlapping event
                            conflicts = True
                            break

                    # If no conflict, add to slots
                    if not conflicts:
                        user_slots.setdefault(date_str, [])
                        user_slots[date_str].append(f"{start_time.strftime('%I:%M%p')}-{end_time.strftime('%I:%M%p')}")

                current_date += timedelta(days=1)

        # Append this user's slots to the overall availability
        user_availability.append(user_slots)

    # Calculate common availability
    common_availability = {}

    # Iterate over the date range
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%d-%m-%Y')

        # Collect slots from all users for this date
        daily_slots = []
        for user_slots in user_availability:
            if date_str in user_slots:
                daily_slots.append(set(user_slots[date_str]))

        # If no slots for all users, skip this date
        if len(daily_slots) < len(user_ids):
            current_date += timedelta(days=1)
            continue

        # Intersect slots to find common availability
        common_slots = set.intersection(*daily_slots) if daily_slots else set()
        if common_slots:
            common_availability[date_str] = list(common_slots)

        current_date += timedelta(days=1)

    return common_availability



