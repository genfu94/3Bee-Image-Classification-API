from tensorflow.keras.applications.resnet50 import (
    decode_predictions,
    preprocess_input,
)
from tensorflow.keras.preprocessing import image
import numpy as np


def predict_image(model, img):
    img = img.resize((224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    predictions = model.predict(img_array)
    decoded_predictions = decode_predictions(predictions, top=1)[0]

    return decoded_predictions
