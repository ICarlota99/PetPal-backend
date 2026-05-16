"""Seed species and breeds. Run: python -m app.seed.seed_db"""

from app.database import SessionLocal, engine, Base
from app.models import Breed, Species
from app.seed.breeds import breeds


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Species).count() > 0:
            print("Database already seeded.")
            return

        for species_name, breed_names in breeds.items():
            species = Species(name=species_name)
            db.add(species)
            db.flush()
            for breed_name in breed_names:
                db.add(Breed(species_id=species.id, name=breed_name))
        db.commit()
        print("Seed completed.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
