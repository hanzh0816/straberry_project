import os
import time
import cv2
import numpy as np

from feature_extractor import *


def get_features(image: np.ndarray, mask: np.ndarray) -> dict:
    """
    获取图像的所有特征
    """
    # 前处理
    image = wavelet_denoise(image)
    image = meidian_denoise(image)

    # 获取特征
    features = {}
    features["coloration"] = get_coloration(image, mask)
    features["texture"] = get_texture_detail(image)
    features["defect"] = get_defect_area(image, mask)
    features["RGB"] = get_RGB_data(image, mask)
    features["aspect"] = get_aspect_ratio(mask)
    return features


def decide_tree_level(image, mask):
    # todo: 改成决策树逻辑
    features = get_features(image, mask)
    coloration = features["coloration"]
    defect_num, defect_ratio = features["defect"]
    aspect_ratio, w, h = features["aspect"]
    texture_level = features["texture"]

    coloration_level = 0
    texture_level = 0
    aspect_level = 0
    defect_level = 0
    if coloration > 0.95:  # 着色度>95%
        coloration_level = 1
    elif coloration > 0.9:  # 着色度>90%
        coloration_level = 2
    else:
        coloration_level = 3

    if defect_num < 3 or defect_ratio < 0.15:  # 缺陷个数小于3 或者缺陷面积比<15%
        defect_level = 1
    elif defect_num < 5 or defect_level < 0.2:  # 缺陷个数小于5 或者缺陷面积比<20%
        defect_level = 2
    else:
        defect_level = 3

    # TODO: 判断长宽的条件，长度与像素相统一
    if w > 500 and h > 400:
        aspect_level = 1
    elif 450 < w < 500 and 350 < h < 400:
        aspect_level = 2
    else:
        aspect_level = 3

    # todo: 增加纹理逻辑判断
    texture_level = 1

    level = int(
        np.floor((coloration_level + texture_level + aspect_level + defect_level) / 4)
    )
    return (
        level,
        texture_level,
        coloration,
        defect_num,
        defect_ratio,
        aspect_ratio,
    )

