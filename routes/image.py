from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from .auth import validate_token_and_get_active_user
from typing import Annotated
from services.image import predict_image
from tensorflow.keras.applications.resnet50 import ResNet50
import uuid
from PIL import Image
import io
import base64


def image_to_base64(img):
    image_byte_array = io.BytesIO()
    img.save(image_byte_array, format="JPEG")
    image_bytes = image_byte_array.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    return image_base64


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
    img_b64 = image_to_base64(img)

    prediction = predict_image(resnet_model, img)[0][1]
    return prediction
