from PIL import Image
import torch
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import numpy as np
from timm.data.constants import IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD

transform = transforms.Compose(
    [
        # transforms.RandomCrop(2048, padding=4),  # 随机裁剪并填充到指定大小
        # transforms.Resize(size=(224, 224)),
        # transforms.RandomHorizontalFlip(),  # 随机水平翻转
        transforms.ToTensor(),  # 转换为张量
        transforms.Normalize(IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD),
        # transforms.Normalize(
        #     mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
        # ),  # 归一化
    ]
)

image = Image.open("1.jpg")  # 替换为实际的图像路径
transformed_image = transform(image)


# 将张量转换为NumPy数组
np_image = transformed_image.numpy()

# 调整通道顺序
np_image = np.transpose(np_image, (1, 2, 0))

# 显示图像
plt.imshow(transformed_image.permute(1, 2, 0))  # 调整通道顺序
plt.axis("off")  # 关闭坐标轴
plt.show()

pil_image = transforms.ToPILImage()(transformed_image)

# 保存图像文件
pil_image.save("output.jpg")  # 替换为你想保存的文件路径和名称
