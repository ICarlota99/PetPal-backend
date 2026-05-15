import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status

from app.config import settings

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_FILE_SIZE = 6 * 1024 * 1024


def is_configured() -> bool:
    return bool(
        settings.cloudinary_cloud_name
        and settings.cloudinary_api_key
        and settings.cloudinary_api_secret
    )


def configure_cloudinary() -> None:
    if is_configured():
        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
            secure=True,
        )


def _validate_image(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image format")


async def upload_image(file: UploadFile, folder: str) -> dict[str, str]:
    if not is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cloudinary is not configured. Add CLOUDINARY_* vars to .env or submit without a photo.",
        )

    _validate_image(file)
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds 6MB limit")

    try:
        result = cloudinary.uploader.upload(
            content,
            folder=f"petpal/{folder}",
            resource_type="image",
        )
        return {"url": result["secure_url"], "public_id": result["public_id"]}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {exc}",
        ) from exc


def delete_image(public_id: str | None) -> None:
    if not public_id or not settings.cloudinary_cloud_name:
        return
    try:
        cloudinary.uploader.destroy(public_id)
    except Exception:
        pass
