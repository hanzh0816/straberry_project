import os
import cv2
import numpy as np
import matplotlib.pyplot as plt


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


os.chdir(os.path.dirname(__file__))
# 加载草莓图像
image = cv2.imread("ZJ_193_ROI.png")
threshold_area = 1000

# 将图像转换为HSV颜色空间
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 定义黄褐色范围的阈值
lower_yellow = np.array([12, 0, 0])  # 根据实际情况调整下界阈值
upper_yellow = np.array([45, 255, 255])  # 根据实际情况调整上界阈值

# 创建黄褐色范围的掩膜
mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

# 执行形态学操作，去除噪声和平滑边缘
kernel = np.ones((5, 5), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

# 寻找并标记图像中的缺陷轮廓
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 创建一个与原始图像大小相同的空白掩膜
blank_mask = np.zeros_like(mask)

# 绘制缺陷轮廓
defect_contours = []
for contour in contours:
    area = cv2.contourArea(contour)
    if area > threshold_area:  # 根据实际情况调整面积阈值
        defect_contours.append(contour)
        cv2.drawContours(blank_mask, [contour], 0, 255, -1)

edges = cv2.Canny(blank_mask, 50, 150)
defect_area = cv2.countNonZero(edges)

print(len(defect_contours))
print(defect_area)
# 显示机械损伤
show(image, edges)
