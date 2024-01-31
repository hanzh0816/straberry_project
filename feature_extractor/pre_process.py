import cv2
import os
import pywt
import numpy as np
import matplotlib.pyplot as plt


def wavelet_denoise(
    image: np.ndarray,
    wavelet: str = "haar",
    auto_level: bool = True,
    noise_sigma: float = 0.25,
) -> cv2.Mat:
    """
    使用自适应level的小波变换与复原对图像进行降噪
    :image (ndarray): 输入图像
    :wavelet (str): 选择的小波变换
    :auto_level (bool): 是否自动选择level
    :noise_sigma (float): 噪声标准差(估计阈值)
    :return (ndarray): 降噪后的图像
    """
    levels = int(np.floor(np.log2(image.shape[0])))
    out = image.copy()
    for i in range(3):
        single_input = image.copy()
        single_input = single_input[:, :, i]

        wc = pywt.wavedec2(single_input, wavelet, level=levels)
        arr, coeff_slices = pywt.coeffs_to_array(wc)
        arr = pywt.threshold(arr, noise_sigma, mode="soft")
        nwc = pywt.array_to_coeffs(arr, coeff_slices, output_format="wavedec2")
        out[:, :, i] = pywt.waverec2(nwc, wavelet)
    # out = np.clip(out, 0, 1)
    return out


def meidian_denoise(image: np.ndarray, win: int = 5) -> np.ndarray:
    """
    使用中值滤波器对图像进行降噪
    :image (ndarray): 输入图像
    :win (int): 中值滤波器窗口大小
    :return (ndarray): 降噪后的图像
    """
    denoised_image = cv2.medianBlur(image, win)
    return denoised_image

