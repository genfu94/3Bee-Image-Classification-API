from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from .auth import validate_token_and_get_active_user
from typing import Annotated
from services.image import predict_image
from tensorflow.keras.applications.resnet50 import ResNet50
import uuid
from PIL import Image
import io

router = APIRouter(prefix="")
resnet_model = ResNet50(weights="imagenet")

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
    # to open the image using PIL.
    if not file.content_type.startswith("image/"):
        return JSONResponse(
            content={"error": "Invalid file format. Only images are allowed."},
            status_code=400,
        )

    request_object_content = await file.read()
    img = Image.open(io.BytesIO(request_object_content))

    predictions = predict_image(resnet_model, img)
    return predictions[0][1]
