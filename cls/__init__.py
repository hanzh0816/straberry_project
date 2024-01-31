from .predict import _predict, _init_predict
from .models import build_model

processor, model = _init_predict()


def predict_image(image):
    return _predict(image, processor, model)
