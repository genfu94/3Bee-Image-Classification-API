from sqlalchemy.orm import Session
from models import Prediction, User
from datetime import datetime


def get_predictions_by_username(db: Session, username: str) -> list[Prediction]:
    user_predictions = db.query(User).filter_by(username=username).first()

    if user_predictions:
        return user_predictions.predictions

    return []


def get_prediction_by_id(db: Session, username: str, prediction_id: int):
    user = db.query(User).filter_by(username=username).first()

    return db.query(Prediction).filter_by(id=prediction_id, user_id=user.id).first()


def add_prediction(
    db: Session, username: str, image_b64: str, prediction_class: str, class_desc: str
):
    user = db.query(User).filter_by(username=username).first()

    if user:
        # Create a new Prediction instance
        prediction = Prediction(
            user_id=user.id,
            image_b64=image_b64,
            prediction_class=prediction_class,
            class_desc=class_desc,
            dt=datetime.now(),  # Set datetime to the current time
        )

        # Add the prediction to the user's predictions and commit the changes
        user.predictions.append(prediction)
        db.add(prediction)
        db.commit()
        db.refresh(
            prediction
        )  # Refresh to populate the instance with database-generated values

        return prediction

    return None
