from .vision_transformer import create_ViT_model, save_ViT_model
from .resnet import create_resnet_model, save_resnet_model


def build_model(config):
    processor = None
    if config.MODEL.TYPE == "ViT":
        processor, model = create_ViT_model(config)
    elif config.MODEL.TYPE == "ResNet":
        processor, model = create_resnet_model(config)
    else:
        raise NotImplementedError
    return processor, model


def save_model(model, config):
    if config.MODEL.TYPE == "ViT":
        save_ViT_model(model, config)
    elif config.MODEL.TYPE == "ResNet":
        save_resnet_model(model, config)
    else:
        raise NotImplementedError
