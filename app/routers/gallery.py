from datetime import date

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_owned_pet
from app.models import Pet, Photo
from app.schemas.gallery import PhotoOut
from app.services.cloudinary import delete_image, upload_image

router = APIRouter(prefix="/pets/{pet_id}/photos", tags=["gallery"])


@router.get("", response_model=list[PhotoOut])
def list_photos(pet: Pet = Depends(get_owned_pet), db: Session = Depends(get_db)):
    return (
        db.query(Photo)
        .filter(Photo.pet_id == pet.id)
        .order_by(Photo.date_uploaded.desc())
        .all()
    )


@router.post("", response_model=PhotoOut, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    title: str | None = Form(None),
    date_uploaded: date = Form(...),
    image: UploadFile = File(...),
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    uploaded = await upload_image(image, f"users/{pet.user_id}/pets/{pet.id}/gallery")
    photo = Photo(
        pet_id=pet.id,
        image_url=uploaded["url"],
        public_id=uploaded["public_id"],
        title=title,
        date_uploaded=date_uploaded,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    photo_id: int,
    pet: Pet = Depends(get_owned_pet),
    db: Session = Depends(get_db),
):
    photo = db.query(Photo).filter(Photo.id == photo_id, Photo.pet_id == pet.id).first()
    if photo is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Photo not found")
    delete_image(photo.public_id)
    db.delete(photo)
    db.commit()
