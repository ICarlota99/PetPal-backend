from datetime import date

from pydantic import BaseModel, Field


class LogCreate(BaseModel):
    title: str | None = Field(default=None, max_length=150)
    content: str = Field(min_length=1)
    date_uploaded: date


class LogUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=150)
    content: str | None = Field(default=None, min_length=1)
    date_uploaded: date | None = None


class LogOut(BaseModel):
    id: int
    pet_id: int
    title: str | None = None
    content: str
    date_uploaded: date

    model_config = {"from_attributes": True}
