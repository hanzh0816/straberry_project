import os
import json
import torch
import torch.nn as nn
from torchvision.models import VisionTransformer
from transformers import ViTImageProcessor, ViTForImageClassification


def create_ViT_model(config):
    model = ViTForImageClassification.from_pretrained(
        config.MODEL.PRETRAINED_PATH, ignore_mismatched_sizes=True
    )
    if config.EVAL_MODE == False:
        model.classifier = nn.Linear(config.MODEL.EMBED_DIM, config.MODEL.NUM_CLASSES)
        processor = ViTImageProcessor(do_resize=False, do_rescale=False)
    else:
        processor = ViTImageProcessor()
    processor.from_pretrained(config.MODEL.PRETRAINED_PATH)
    return processor, model


def save_ViT_model(model, config):
    save_path = os.path.join(config.OUTPUT, config.MODEL.NAME, "checkpoint")
    model.save_pretrained(save_path)
