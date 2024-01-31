import os
import cv2
import pywt
import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import graycomatrix, graycoprops


def show(image1, image2):
    image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)
    image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 6))
    ax1, ax2 = axes
    ax1.imshow(image1)
    ax2.imshow(image2)
    ax1.set_title("Original Image")
    ax2.set_title("Denoised Image")
    ax1.axis("off")
    ax2.axis("off")
    # 调整子图布局
    plt.tight_layout()
    # 显示所有子图
    plt.show()


def mask2gray(mask: np.ndarray) -> np.ndarray:
    # 将掩膜乘以255，将0变为0，将1变为255
    mask = mask * 255
    # 创建全零矩阵，作为灰度图像的初始形状
    gray_image = np.zeros((mask.shape[0], mask.shape[1]), dtype=np.uint8)
    # 将掩膜的值赋给灰度图像的像素值
    gray_image[:, :] = mask
    return gray_image


def get_area(mask: np.ndarray) -> int:
    """
    根据掩膜图像计算面积
    :mask (ndarray): 掩膜图像
    :return (float): 面积(像素个数)
    """

    gray_mask = mask2gray(mask)
    _, thresholded_mask = cv2.threshold(gray_mask, 1, 255, cv2.THRESH_BINARY)
    area = cv2.countNonZero(thresholded_mask)
    return area


def get_coloration(
    image: np.ndarray,
    mask: np.ndarray,
) -> float:
    """
    计算着色度
    :image (ndarray): 输入图像
    :mask (ndarray): 掩膜图像
    :return (float): 着色度百分比
    """
    image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    red_lower = np.array([0, 100, 100])  # 下界阈值
    red_upper = np.array([10, 255, 255])  # 上界阈值
    # 创建红色范围的掩膜
    red_mask = cv2.inRange(image_hsv, red_lower, red_upper)

    # 统计红色范围内的像素数量
    red_pixels = cv2.countNonZero(red_mask)
    # 计算着色度
    total_pixels = get_area(mask)
    color_ratio = red_pixels / total_pixels
    return color_ratio


def get_texture_detail(image: np.ndarray) -> int:
    """
    计算纹理特征
    :image (ndarray): 输入图像
    :return (list): 纹理细致程度
    """
    # 将图像转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # 计算GLCM矩阵
    glcm = graycomatrix(
        gray, distances=[1], angles=[0], levels=256, symmetric=True, normed=True
    )

    # 计算纹理特征
    contrast = graycoprops(glcm, "contrast")[0, 0]  # 对比度
    homogeneity = graycoprops(glcm, "homogeneity")[0, 0]  # 同质度
    energy = graycoprops(glcm, "energy")[0, 0]  # ASM能
    correlation = graycoprops(glcm, "correlation")[0, 0]  # 相关性
    # print(contrast, homogeneity, energy, correlation)
    # TODO: 计算纹理细致程度
    texture_level = 1
    return texture_level


def get_RGB_data(image: np.ndarray, mask: np.ndarray) -> list:
    """
    计算图像中的像素的各项统计，得到色泽指标
    :image (ndarray): 输入图像
    :mask (ndarray): 掩膜图像
    :return (list): 色泽指标
    """
    col = get_coloration(image, mask)  # 着色度
    _, binary_mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)

    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    masked_h = cv2.bitwise_and(hsv[:, :, 0], binary_mask)
    mean_h = np.mean(masked_h)  # H通道均值
    return col, mean_h


def get_defect_area(image: np.ndarray, mask: np.ndarray):
    """
    计算图像中的缺陷区域的面积(通过H通道阈值判断缺陷，通过边缘检测确定面积)
    :image (ndarray): 输入图像
    :return (int): 缺陷个数,缺陷面积比
    """
    threshold_area = 1000
    # 将图像转换为HSV颜色空间
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    # 定义缺陷颜色范围的阈值
    lower_yellow = np.array([11, 0, 0])  # 根据实际情况调整下界阈值
    upper_yellow = np.array([55, 255, 255])  # 根据实际情况调整上界阈值
    # 创建缺陷颜色范围的掩膜
    defect_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    # 执行形态学操作，去除噪声和平滑边缘
    kernel = np.ones((5, 5), np.uint8)
    defect_mask = cv2.morphologyEx(defect_mask, cv2.MORPH_OPEN, kernel)
    defect_mask = cv2.morphologyEx(defect_mask, cv2.MORPH_CLOSE, kernel)

    # 寻找并标记图像中的缺陷轮廓
    contours, _ = cv2.findContours(
        defect_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    # 创建一个与原始图像大小相同的空白掩膜
    blank_mask = np.zeros_like(defect_mask)

    # 绘制缺陷轮廓
    defect_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > threshold_area:  # 根据实际情况调整面积阈值
            defect_contours.append(contour)
            cv2.drawContours(blank_mask, [contour], 0, 255, -1)

    # show(image, blank_mask)
    edges = cv2.Canny(blank_mask, 50, 150)
    defect_area = cv2.countNonZero(edges)
    total_pixels = get_area(mask)
    defect_ratio = defect_area / total_pixels
    return len(defect_contours), defect_ratio


def get_aspect_ratio(mask: np.ndarray):
    """
    计算果实的长宽比
    :mask (ndarray): 掩膜图像
    :return (list): 长宽比,长度,宽度
    """

    # 查找轮廓
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    # 获取最大轮廓
    max_contour = max(contours, key=cv2.contourArea)
    # 计算轮廓的边界框
    x, y, w, h = cv2.boundingRect(max_contour)
    w, h = max(w, h), min(w, h)
    # 计算长宽比
    aspect_ratio = float(w) / h
    return aspect_ratio, w, h


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    mask = cv2.imread("./ZJ_305_mask.png")
    image = cv2.imread("./ZJ_305_ROI.png")
    get_texture_detail(image)
    get_defect_area(image, mask)
    # print(get_area(mask))
    # print(get_coloration(image, mask))
