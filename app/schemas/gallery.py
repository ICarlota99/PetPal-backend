from datetime import date

from pydantic import BaseModel, Field


class PhotoCreate(BaseModel):
    title: str | None = Field(default=None, max_length=100)
    date_uploaded: date


class PhotoOut(BaseModel):
    id: int
    pet_id: int
    image_url: str
    title: str | None = None
    date_uploaded: date

    model_config = {"from_attributes": True}
