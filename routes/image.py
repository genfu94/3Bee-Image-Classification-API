from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from .auth import validate_token_and_get_active_user
from typing import Annotated

router = APIRouter(prefix="")

MAX_FILE_SIZE_MB = 30 * 1024 * 1024


@router.post("/predict")
async def upload_image(
    username: Annotated[str, Depends(validate_token_and_get_active_user)],
    file: UploadFile = File(...),
):
    if file.size > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400, detail="File size exceeds the maximum allowed (30MB)"
        )

    # TODO: Here we only check based on file extension. We should check by trying
    # to open the image.
    if not file.content_type.startswith("image/"):
        return JSONResponse(
            content={"error": "Invalid file format. Only images are allowed."},
            status_code=400,
        )

    # TODO: Do processing
    return file.filename
