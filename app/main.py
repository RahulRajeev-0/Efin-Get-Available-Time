# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import crud, models, schemas
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import date, datetime

# Create the tables in the database
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# POST endpoint to create a new user
@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)


@app.post("/general-availability/", response_model=schemas.GeneralAvailabilityResponse)
def create_general_availability(availability: schemas.GeneralAvailabilityCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_general_availability(db=db, availability=availability)
    except HTTPException as e:
        print("ERROR = ",e)
        raise HTTPException(status_code=400, detail="This availability already exists for the user or have overlaps with an existing availability")
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Database constraint violation error.")
    except Exception as e:
        # Log any unexpected errors and return a generic 500 error
        logging.error(f"Unexpected error: {str(e)}")


@app.post("/custom-availability/", response_model=schemas.CustomAvailabilityResponse)
def create_custom_availability(availability: schemas.CustomAvailabilityCreate, db: Session = Depends(get_db)):
    return crud.create_custom_availability(db=db, availability=availability)
    

# ANSWER ENDPOINT (MAIN ENDPOINT MENSTIONED IN TASK)
@app.post("/common-availability/")
def get_common_availability(payload: schemas.AvailabilityRequest, db: Session = Depends(get_db)):
    user_ids = payload.user_ids
    start_date = payload.startdate
    end_date = payload.enddate
    timezone = payload.timezone

    # Convert input date range to Python's datetime objects for easy manipulation
    start_date_obj = datetime.strptime(start_date, "%d-%m-%Y").date()
    end_date_obj = datetime.strptime(end_date, "%d-%m-%Y").date()

    # Fetch availability for users
    available_slots = crud.get_common_availability(db, user_ids, start_date_obj, end_date_obj, timezone)

    return available_slots




# extra working on 

