from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Breed, Species, User
from app.schemas.pet import BreedOut, SpeciesOut

router = APIRouter(prefix="/species", tags=["species"])


@router.get("", response_model=list[SpeciesOut])
def list_species(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.query(Species).order_by(Species.name).all()


@router.get("/{species_id}/breeds", response_model=list[BreedOut])
def list_breeds(
    species_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.query(Breed).filter(Breed.species_id == species_id).order_by(Breed.name).all()
