from copy import deepcopy
from typing import List
import cv2
import matplotlib.pyplot as plt
import numpy as np


def find_reddest_pixel(_image) -> List:
    """
    找到图像中红色最亮的点作为要分割的主体的中心点(只关心一个物体的分割)
    """
    # 将图像从BGR颜色空间转换为HSV颜色空间
    hsv_image = cv2.cvtColor(_image, cv2.COLOR_BGR2HSV)

    lower_red = cv2.inRange(hsv_image, (0, 100, 100), (30, 255, 255))
    upper_red = cv2.inRange(hsv_image, (150, 100, 100), (180, 255, 255))
    mask_red = cv2.bitwise_or(lower_red, upper_red)
    # print(type(mask_red))

    # red_image = cv2.bitwise_and(_image, _image, mask=mask_red)

    moments = cv2.moments(mask_red)
    centroid_x = int(moments["m10"] / moments["m00"])
    centroid_y = int(moments["m01"] / moments["m00"])

    reddest_pixel = [centroid_x, centroid_y]
    return reddest_pixel


def show_points(coords, labels, ax, marker_size=375):
    """
    在画布上显示正负点的坐标
    """
    pos_points = coords[labels == 1]
    neg_points = coords[labels == 0]
    ax.scatter(
        pos_points[:, 0],
        pos_points[:, 1],
        color="green",
        marker="*",
        s=marker_size,
        edgecolor="white",
        linewidth=1.25,
    )
    ax.scatter(
        neg_points[:, 0],
        neg_points[:, 1],
        color="red",
        marker="*",
        s=marker_size,
        edgecolor="white",
        linewidth=1.25,
    )


def save_mask(mask, save_path, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([220, 20, 60])
    h, w = mask.shape[-2:]

    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    cv2.imwrite(save_path, mask_image)
