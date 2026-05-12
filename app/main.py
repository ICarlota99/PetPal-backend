from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, gallery, logs, pets, species, trackers
from app.services.cloudinary import configure_cloudinary

configure_cloudinary()

app = FastAPI(
    title="PetPal API",
    description="REST API for pet care management",
    version="1.0.0",
)

# Local dev: allow any localhost port (Next.js may use 3000, 3001, 3002, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(species.router, prefix="/api")
app.include_router(pets.router, prefix="/api")
app.include_router(gallery.router, prefix="/api")
app.include_router(logs.router, prefix="/api")
app.include_router(trackers.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
