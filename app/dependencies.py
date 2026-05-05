from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Pet, User
from app.services.auth import decode_access_token, get_user_by_id

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_owned_pet(
    pet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Pet:
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if pet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")
    if pet.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this pet")
    return pet
