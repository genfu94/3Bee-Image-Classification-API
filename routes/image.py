from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from .auth import validate_token_and_get_active_user, get_db
from typing import Annotated
from services.image import predict_image
from db_crud.image import (
    get_predictions_by_username,
    add_prediction,
    get_prediction_by_id,
)
from tensorflow.keras.applications.resnet50 import ResNet50
from PIL import Image
import io
import base64
from sqlalchemy.orm import Session
import requests


def get_class_description_from_wiki(pred_class: str):
    base_url = "https://en.wikipedia.org/w/api.php"

    params = {
        "format": "json",
        "action": "query",
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "redirects": 1,
        "titles": pred_class,
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        pages = response.json()["query"]["pages"]

        page_id, page_info = next(iter(pages.items()))

        return page_info["extract"]

    return None


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
async def predict(
    username: Annotated[str, Depends(validate_token_and_get_active_user)],
    db: Session = Depends(get_db),
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

    try:
        request_object_content = await file.read()
        img = Image.open(io.BytesIO(request_object_content))
        img_b64 = image_to_base64(img)
    except:
        return HTTPException(400, "There was an error reading the image")

    try:
        predictions = predict_image(resnet_model, img)
    except:
        return HTTPException(400, "There was an error processing the image")

    prediction = predictions[0][1]
    desc = get_class_description_from_wiki(prediction)
    add_prediction(db, username, img_b64, prediction, desc)
    return prediction


@router.get("/predictions")
async def get_predictions(
    username: Annotated[str, Depends(validate_token_and_get_active_user)],
    db: Session = Depends(get_db),
):
    return get_predictions_by_username(db, username)


@router.get("/predictions/{ID}")
async def get_predictions(
    ID: int,
    username: Annotated[str, Depends(validate_token_and_get_active_user)],
    db: Session = Depends(get_db),
):
    return get_prediction_by_id(db, username, ID)
