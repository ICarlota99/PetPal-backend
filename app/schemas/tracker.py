from datetime import date

from pydantic import BaseModel, Field


class WeightCreate(BaseModel):
    weight_in_kg: float = Field(gt=0)
    date: date
    notes: str | None = Field(default=None, max_length=100)


class VaccineCreate(BaseModel):
    vaccine_name: str = Field(min_length=1, max_length=100)
    date: date
    next_dosis: date | None = None
    administered_by: str | None = Field(default=None, max_length=150)
    notes: str | None = Field(default=None, max_length=100)


class DewormingCreate(BaseModel):
    product_name: str = Field(min_length=1, max_length=100)
    date: date
    next_dosis: date | None = None
    notes: str | None = Field(default=None, max_length=100)


class MedicationCreate(BaseModel):
    product_name: str = Field(min_length=1, max_length=100)
    date: date
    next_dosis: date | None = None
    notes: str | None = Field(default=None, max_length=100)


class TrackerEntryOut(BaseModel):
    id: int
    pet_id: int
    date: date
    notes: str | None = None

    model_config = {"from_attributes": True}


class WeightOut(TrackerEntryOut):
    weight_in_kg: float


class VaccineOut(TrackerEntryOut):
    vaccine_name: str
    next_dosis: date | None = None
    administered_by: str | None = None


class DewormingOut(TrackerEntryOut):
    product_name: str
    next_dosis: date | None = None


class MedicationOut(TrackerEntryOut):
    product_name: str
    next_dosis: date | None = None


class WeightChartPoint(BaseModel):
    date: date
    weight_in_kg: float | None = None


class WeightChartOut(BaseModel):
    year: int
    month: int
    month_name: str
    points: list[WeightChartPoint]
