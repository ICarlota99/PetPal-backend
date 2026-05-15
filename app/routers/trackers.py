import calendar
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_owned_pet
from app.models import (
    ExternalDewormingTracker,
    InternalDewormingTracker,
    MedicationTracker,
    Pet,
    VaccineTracker,
    WeightTracker,
)
from app.schemas.tracker import (
    DewormingCreate,
    DewormingOut,
    MedicationCreate,
    MedicationOut,
    VaccineCreate,
    VaccineOut,
    WeightChartOut,
    WeightChartPoint,
    WeightCreate,
    WeightOut,
)

router = APIRouter(prefix="/pets/{pet_id}/trackers", tags=["trackers"])

TRACKER_MODELS = {
    "weight": WeightTracker,
    "vaccine": VaccineTracker,
    "internal_deworming": InternalDewormingTracker,
    "external_deworming": ExternalDewormingTracker,
    "medication": MedicationTracker,
}


@router.get("/{tracker_type}")
def list_tracker_entries(
    tracker_type: str,
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    model = TRACKER_MODELS.get(tracker_type)
    if model is None:
        raise HTTPException(status_code=400, detail="Invalid tracker type")
    return db.query(model).filter(model.pet_id == pet.id).order_by(model.date.desc()).all()


@router.post("/weight", response_model=WeightOut, status_code=status.HTTP_201_CREATED)
def add_weight(
    payload: WeightCreate,
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    entry = WeightTracker(pet_id=pet.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.post("/vaccine", response_model=VaccineOut, status_code=status.HTTP_201_CREATED)
def add_vaccine(
    payload: VaccineCreate,
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    entry = VaccineTracker(pet_id=pet.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.post("/internal_deworming", response_model=DewormingOut, status_code=status.HTTP_201_CREATED)
def add_internal_deworming(
    payload: DewormingCreate,
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    entry = InternalDewormingTracker(pet_id=pet.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.post("/external_deworming", response_model=DewormingOut, status_code=status.HTTP_201_CREATED)
def add_external_deworming(
    payload: DewormingCreate,
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    entry = ExternalDewormingTracker(pet_id=pet.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.post("/medication", response_model=MedicationOut, status_code=status.HTTP_201_CREATED)
def add_medication(
    payload: MedicationCreate,
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    entry = MedicationTracker(pet_id=pet.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{tracker_type}/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tracker_entry(
    tracker_type: str,
    entry_id: int,
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    model = TRACKER_MODELS.get(tracker_type)
    if model is None:
        raise HTTPException(status_code=400, detail="Invalid tracker type")

    entry = db.query(model).filter(model.id == entry_id, model.pet_id == pet.id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()


@router.get("/weight/chart", response_model=WeightChartOut)
def weight_chart(
    month: int | None = None,
    year: int | None = None,
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    month = month or now.month
    year = year or now.year

    entries = (
        db.query(WeightTracker)
        .filter(WeightTracker.pet_id == pet.id)
        .order_by(WeightTracker.date)
        .all()
    )
    weight_by_date = {
        e.date: e.weight_in_kg
        for e in entries
        if e.date.month == month and e.date.year == year
    }

    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    all_days = [
        first_day + timedelta(days=i)
        for i in range((last_day - first_day).days + 1)
    ]

    points = [
        WeightChartPoint(date=day, weight_in_kg=weight_by_date.get(day))
        for day in all_days
    ]

    return WeightChartOut(
        year=year,
        month=month,
        month_name=first_day.strftime("%B"),
        points=points,
    )
