from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_owned_pet
from app.models import Log, Pet
from app.schemas.log import LogCreate, LogOut, LogUpdate

router = APIRouter(prefix="/pets/{pet_id}/logs", tags=["logs"])


@router.get("", response_model=list[LogOut])
def list_logs(pet: Pet = Depends(get_owned_pet), db: Session = Depends(get_db)):
    return db.query(Log).filter(Log.pet_id == pet.id).order_by(Log.date_uploaded.desc()).all()


@router.post("", response_model=LogOut, status_code=status.HTTP_201_CREATED)
def create_log(
    payload: LogCreate,
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    log = Log(pet_id=pet.id, **payload.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/{log_id}", response_model=LogOut)
def get_log(
    log_id: int,
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    log = db.query(Log).filter(Log.id == log_id, Log.pet_id == pet.id).first()
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


@router.put("/{log_id}", response_model=LogOut)
def update_log(
    log_id: int,
    payload: LogUpdate,
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    log = db.query(Log).filter(Log.id == log_id, Log.pet_id == pet.id).first()
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(log, key, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(
    log_id: int,
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    log = db.query(Log).filter(Log.id == log_id, Log.pet_id == pet.id).first()
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(log)
    db.commit()
