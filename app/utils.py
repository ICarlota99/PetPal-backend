from datetime import date

from app.models import Pet
from app.schemas.pet import PetOut


def calculate_age(birth_date: date | None) -> int | None:
    if not birth_date:
        return None
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def pet_to_out(pet: Pet) -> PetOut:
    return PetOut(
        id=pet.id,
        user_id=pet.user_id,
        name=pet.name,
        birth_date=pet.birth_date,
        adoption_date=pet.adoption_date,
        sex=pet.sex,
        species_id=pet.species_id,
        breed_id=pet.breed_id,
        sterilized=pet.sterilized,
        microchip_number=pet.microchip_number,
        insurance_company=pet.insurance_company,
        insurance_number=pet.insurance_number,
        pet_profile_photo=pet.pet_profile_photo,
        species_name=pet.species.name if pet.species else None,
        breed_name=pet.breed.name if pet.breed else None,
        age=calculate_age(pet.birth_date),
    )
