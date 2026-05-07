from datetime import date

from pydantic import BaseModel, Field


class SpeciesOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class BreedOut(BaseModel):
    id: int
    name: str
    species_id: int

    model_config = {"from_attributes": True}


class PetBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    birth_date: date | None = None
    adoption_date: date | None = None
    sex: str = Field(pattern=r"^[MF]$")
    species_id: int
    breed_id: int | None = None
    sterilized: bool = False
    microchip_number: str | None = Field(default=None, max_length=50)
    insurance_company: str | None = Field(default=None, max_length=100)
    insurance_number: str | None = Field(default=None, max_length=50)


class PetCreate(PetBase):
    pass


class PetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    birth_date: date | None = None
    adoption_date: date | None = None
    sex: str | None = Field(default=None, pattern=r"^[MF]$")
    species_id: int | None = None
    breed_id: int | None = None
    sterilized: bool | None = None
    microchip_number: str | None = Field(default=None, max_length=50)
    insurance_company: str | None = Field(default=None, max_length=100)
    insurance_number: str | None = Field(default=None, max_length=50)
    pet_profile_photo: str | None = None


class PetOut(PetBase):
    id: int
    user_id: int
    pet_profile_photo: str | None = None
    species_name: str | None = None
    breed_name: str | None = None
    age: int | None = None

    model_config = {"from_attributes": True}
