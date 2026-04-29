from datetime import date, datetime

from sqlalchemy import Boolean, CheckConstraint, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    pw_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    pets: Mapped[list["Pet"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Species(Base):
    __tablename__ = "species"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    breeds: Mapped[list["Breed"]] = relationship(back_populates="species", cascade="all, delete-orphan")


class Breed(Base):
    __tablename__ = "breeds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    species_id: Mapped[int] = mapped_column(ForeignKey("species.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    species: Mapped["Species"] = relationship(back_populates="breeds")


class Pet(Base):
    __tablename__ = "pets"
    __table_args__ = (CheckConstraint("sex IN ('M', 'F')", name="check_pet_sex"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pet_profile_photo: Mapped[str | None] = mapped_column(String(500), nullable=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    adoption_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sex: Mapped[str] = mapped_column(String(1), nullable=False)
    species_id: Mapped[int] = mapped_column(ForeignKey("species.id", ondelete="CASCADE"), nullable=False, index=True)
    breed_id: Mapped[int | None] = mapped_column(ForeignKey("breeds.id", ondelete="SET NULL"), nullable=True, index=True)
    sterilized: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    microchip_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    insurance_company: Mapped[str | None] = mapped_column(String(100), nullable=True)
    insurance_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    owner: Mapped["User"] = relationship(back_populates="pets")
    species: Mapped["Species"] = relationship()
    breed: Mapped["Breed | None"] = relationship()
    photos: Mapped[list["Photo"]] = relationship(back_populates="pet", cascade="all, delete-orphan")
    logs: Mapped[list["Log"]] = relationship(back_populates="pet", cascade="all, delete-orphan")
    weight_tracks: Mapped[list["WeightTracker"]] = relationship(back_populates="pet", cascade="all, delete-orphan")
    vaccines: Mapped[list["VaccineTracker"]] = relationship(back_populates="pet", cascade="all, delete-orphan")
    internal_deworm: Mapped[list["InternalDewormingTracker"]] = relationship(back_populates="pet", cascade="all, delete-orphan")
    external_deworm: Mapped[list["ExternalDewormingTracker"]] = relationship(back_populates="pet", cascade="all, delete-orphan")
    medications: Mapped[list["MedicationTracker"]] = relationship(back_populates="pet", cascade="all, delete-orphan")


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    public_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    title: Mapped[str | None] = mapped_column(String(100))
    date_uploaded: Mapped[date] = mapped_column(Date, nullable=False)

    pet: Mapped["Pet"] = relationship(back_populates="photos")


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str | None] = mapped_column(String(150))
    date_uploaded: Mapped[date] = mapped_column(Date, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    pet: Mapped["Pet"] = relationship(back_populates="logs")


class WeightTracker(Base):
    __tablename__ = "weight_tracker"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)
    weight_in_kg: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(100), nullable=True)

    pet: Mapped["Pet"] = relationship(back_populates="weight_tracks")


class VaccineTracker(Base):
    __tablename__ = "vaccine_tracker"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)
    vaccine_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    next_dosis: Mapped[date | None] = mapped_column(Date, nullable=True)
    administered_by: Mapped[str | None] = mapped_column(String(150), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(100), nullable=True)

    pet: Mapped["Pet"] = relationship(back_populates="vaccines")


class InternalDewormingTracker(Base):
    __tablename__ = "internal_deworming_tracker"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    next_dosis: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(100), nullable=True)

    pet: Mapped["Pet"] = relationship(back_populates="internal_deworm")


class ExternalDewormingTracker(Base):
    __tablename__ = "external_deworming_tracker"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    next_dosis: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(100), nullable=True)

    pet: Mapped["Pet"] = relationship(back_populates="external_deworm")


class MedicationTracker(Base):
    __tablename__ = "medication_tracker"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    next_dosis: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(100), nullable=True)

    pet: Mapped["Pet"] = relationship(back_populates="medications")
