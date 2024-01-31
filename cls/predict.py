import os
import cv2
import yaml
from PIL import Image
import numpy as np
import torch
import torchvision.transforms as transforms
import torch.nn.functional as F
from yacs.config import CfgNode as CN

from .models import build_model

id2label = ["HY", "NY", "ZJ"]


def get_confg():
    _C = CN()
    _C.BASE = [""]
    _C.EVAL_MODE = True

    _C.MODEL = CN()
    _C.MODEL.NAME = "vit-base-patch16-224"
    _C.MODEL.TYPE = "ViT"
    _C.MODEL.PRETRAINED = True
    _C.MODEL.PRETRAINED_PATH = r"D:\Files\model\huggingface\checkpoint"
    _C.MODEL.EMBED_DIM = 768
    _C.MODEL.NUM_CLASSES = 3

    config = _C.clone()
    config.freeze()
    return config


def _init_predict():
    print("init predictor configs")
    config = get_confg()
    print("loading model")
    processor, model = build_model(config)
    model.eval()

    return processor, model


def image2tensor(image):
    # rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # image: RGB格式
    input_tensor = torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0)
    # print(input_tensor.shape)
    return input_tensor


def _predict(image: np.ndarray, processor, model):
    inputs = image2tensor(image)
    inputs = processor(images=inputs, return_tensors="pt")
    inputs["pixel_values"] = inputs["pixel_values"]

    outputs = model(**inputs)
    logits = outputs.logits
    predict = F.softmax(logits, dim=1)

    predict_label = torch.argmax(predict, dim=1)
    predict_label = predict_label.squeeze()
    # print(predict_label.item())
    # print(id2label[predict_label.item()])
    return id2label[predict_label.item()]
