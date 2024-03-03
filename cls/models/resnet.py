import os
import json
import torch
import torch.nn as nn
from transformers import AutoFeatureExtractor, ResNetForImageClassification


def create_resnet_model(config):
    processor = AutoFeatureExtractor.from_pretrained(config.MODEL.PRETRAINED_PATH)
    if config.MODEL.PRETRAINED == True:
        model = ResNetForImageClassification.from_pretrained(
            config.MODEL.PRETRAINED_PATH
        )
    else:
        with open(os.path.join(config.MODEL.PRETRAINED_PATH, "config.json"), "r") as f:
            resnet_config = json.load(f)
            model = ResNetForImageClassification(config=resnet_config)

    model.classifier = nn.Sequential(
        nn.Flatten(), nn.Linear(config.MODEL.EMBED_DIM, config.MODEL.NUM_CLASSES)
    )
    return processor, model
    # ViT_model = VisionTransformer(
    #     image_size=config.DATA.IMAGE_SIZE,
    #     patch_size=config.MODEL.PATCH_SIZE,
    #     num_layers=config.MODEL.NUM_LAYERS,
    #     num_heads=config.MODEL.NUM_HEADS,
    #     hidden_dim=config.MODEL.EMBED_DIM,
    #     mlp_dim=config.MODEL.MLP_DIM,
    #     num_classes=config.MODEL.NUM_CLASSES,
    # )
    # return ViT_model


def save_resnet_model(model, config):
    save_path = os.path.join(config.OUTPUT, config.MODEL.NAME, "checkpoint")
    model.save_pretrained(save_path)
