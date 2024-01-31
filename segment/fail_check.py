import os
import time
import glob
import time
import cv2
import numpy as np
from utils import *
from segment_anything import sam_model_registry, SamPredictor

scale_ratio = 0.3


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        original_x = int(x / scale_ratio)
        original_y = int(y / scale_ratio)
        param["clicked"] = True
        param["coordinates"] = (int(original_x), int(original_y))
        cv2.destroyAllWindows()


def get_coords(_image):
    # 创建窗口并绑定鼠标回调函数
    cv2.namedWindow("Image")
    callback_params = {"clicked": False, "coordinates": None}
    cv2.setMouseCallback("Image", mouse_callback, callback_params)

    # 显示图像
    small_image = cv2.resize(_image, (0, 0), fx=scale_ratio, fy=scale_ratio)
    cv2.imshow("Image", small_image)

    # 等待用户点击
    while not callback_params["clicked"]:
        cv2.waitKey(10)

    # 获取鼠标点击的坐标
    clicked_coordinates = callback_params["coordinates"]

    # 关闭窗口
    # cv2.destroyAllWindows()

    # 输出鼠标点击的坐标
    print("鼠标点击坐标：", clicked_coordinates)
    return clicked_coordinates


def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30 / 255, 144 / 255, 255 / 255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1)
    mask_image = mask_image.astype(np.float32)

    small_image = cv2.resize(mask_image, (0, 0), fx=scale_ratio, fy=scale_ratio)
    ax.imshow(small_image)


def init() -> SamPredictor:
    sam_checkpoint = "D://Files//checkpoints//SAM//sam_vit_b_01ec64.pth"
    device = "cuda"
    model_type = "vit_b"
    print("loading model")
    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
    sam.to(device=device)
    predictor = SamPredictor(sam)
    print("loading model finished")

    return predictor


def process_image(image_path, mask_save_path, ROI_save_path, predictor):
    """输入image_path, 进行处理，并保存分割图像"""
    image = cv2.imread(image_path)

    reddest_point = find_reddest_pixel(image)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    predictor.set_image(image)

    points = get_coords(image)
    input_point = np.array([[points[0], points[1]]])
    input_label = np.array([1])

    masks, scores, _ = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=True,
    )

    n = len(masks)
    fig, axes = plt.subplots(nrows=n, ncols=1, figsize=(8, 6))

    for i, (mask, score) in enumerate(zip(masks, scores)):
        ax = axes[i]

        ax.imshow(image)
        show_mask(mask, ax)
        # show_points(input_point, input_label, ax)
        ax.set_title(f"Mask {i}, Score: {score:.3f}")
        # ax.title(f"Mask {i+1}, Score: {score:.3f}", fontsize=18)
        ax.axis("off")

    # 调整子图布局
    plt.tight_layout()
    # 显示所有子图
    plt.show()

    idx = input("enter: ")
    best_mask = masks[int(idx)]

    save_mask(best_mask, mask_save_path)
    best_mask = np.array(best_mask, dtype=np.uint8)
    ROI_image = cv2.bitwise_and(image, image, mask=best_mask)
    ROI_image = cv2.cvtColor(ROI_image, cv2.COLOR_RGB2BGR)
    print(ROI_save_path)
    cv2.imwrite(ROI_save_path, ROI_image)


def main():
    predictor = init()
    file_names = []
    with open("./1.txt", "r") as f:
        for line in f.readlines():
            file_names.append(line)

    for file_name in file_names:
        image_file_name = "\\".join(
            file_name.split("\\")[:5] + file_name.split("\\")[6:]
        )
        image_file_name = image_file_name[:-9] + ".jpg"
        mask_file_name = "\\".join(
            file_name.split("\\")[:5] + ["mask"] + file_name.split("\\")[6:]
        )

        mask_file_name = mask_file_name[:-9] + "_mask.png"

        file_name = file_name[:-1]
        # print(mask_file_name)

        process_image(image_file_name, mask_file_name, file_name, predictor)


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    main()
