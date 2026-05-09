from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_owned_pet
from app.models import Pet, User
from app.schemas.pet import PetOut, PetUpdate
from app.services.cloudinary import delete_image, is_configured, upload_image
from app.utils import pet_to_out

router = APIRouter(prefix="/pets", tags=["pets"])


@router.get("", response_model=list[PetOut])
def list_pets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pets = db.query(Pet).filter(Pet.user_id == current_user.id).order_by(Pet.name).all()
    return [pet_to_out(pet) for pet in pets]


@router.post("", response_model=PetOut, status_code=status.HTTP_201_CREATED)
async def create_pet(
    name: str = Form(...),
    sex: str = Form(...),
    species_id: int = Form(...),
    breed_id: str | None = Form(None),
    birth_date: str | None = Form(None),
    adoption_date: str | None = Form(None),
    sterilized: bool = Form(False),
    microchip_number: str | None = Form(None),
    insurance_company: str | None = Form(None),
    insurance_number: str | None = Form(None),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import date as date_type

    def parse_date(value: str | None) -> date_type | None:
        if not value or not value.strip():
            return None
        return date_type.fromisoformat(value)

    profile_url = None
    if photo and photo.filename:
        if not is_configured():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Photo upload requires Cloudinary. Remove the photo or configure CLOUDINARY_* in .env.",
            )
        uploaded = await upload_image(photo, f"users/{current_user.id}/pets")
        profile_url = uploaded["url"]

    pet = Pet(
        user_id=current_user.id,
        name=name,
        sex=sex,
        species_id=species_id,
        breed_id=int(breed_id) if breed_id else None,
        birth_date=parse_date(birth_date),
        adoption_date=parse_date(adoption_date),
        sterilized=sterilized,
        microchip_number=microchip_number,
        insurance_company=insurance_company,
        insurance_number=insurance_number,
        pet_profile_photo=profile_url,
    )
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet_to_out(pet)


@router.get("/{pet_id}", response_model=PetOut)
def get_pet(pet: Pet = Depends(get_owned_pet)):
    return pet_to_out(pet)


@router.put("/{pet_id}", response_model=PetOut)
async def update_pet(
    payload: PetUpdate,
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(pet, key, value)
    db.commit()
    db.refresh(pet)
    return pet_to_out(pet)


@router.post("/{pet_id}/photo", response_model=PetOut)
async def update_pet_photo(
    photo: UploadFile = File(...),
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    uploaded = await upload_image(photo, f"users/{pet.user_id}/pets/{pet.id}")
    if pet.pet_profile_photo and "cloudinary" in (pet.pet_profile_photo or ""):
        # Legacy URLs without public_id are kept; new uploads always use Cloudinary
        pass
    pet.pet_profile_photo = uploaded["url"]
    db.commit()
    db.refresh(pet)
    return pet_to_out(pet)


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    db.delete(pet)
    db.commit()
