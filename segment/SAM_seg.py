import os
import glob
import time
import cv2
import numpy as np
from utils import *
from segment_anything import sam_model_registry, SamPredictor


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
    input_point = np.array([[reddest_point[0], reddest_point[1]]])
    input_label = np.array([1])

    masks, scores, _ = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=True,
    )

    x, y, z = np.array(masks).shape
    threshold = 1e5
    pmask_idx = np.where(np.sum(np.reshape(masks, (x, y * z)), axis=1) > threshold)[0]
    try:
        best_mask_idx = pmask_idx[np.argmax(scores[pmask_idx])]
        best_mask = masks[best_mask_idx]
        print(np.array(best_mask).shape)
    except ValueError:
        best_mask = np.full((y, z), False, dtype=bool)
    # best_score = scores[best_mask_idx]

    # print(type(best_mask))
    save_mask(best_mask, mask_save_path)
    best_mask = np.array(best_mask, dtype=np.uint8)
    ROI_image = cv2.bitwise_and(image, image, mask=best_mask)

    cv2.imwrite(ROI_save_path, cv2.cvtColor(ROI_image, cv2.COLOR_RGB2BGR))


def main():
    predictor = init()

    data_path = r"D://Files//data//Strawberry Pictures"
    dirs_list = os.listdir(data_path)
    cnt = 0
    for dir in dirs_list[1:]:
        if os.path.exists(os.path.join(data_path, dir, "mask")) is False:
            os.mkdir(os.path.join(data_path, dir, "mask"))

        if os.path.exists(os.path.join(data_path, dir, "ROI")) is False:
            os.mkdir(os.path.join(data_path, dir, "ROI"))

        image_paths = glob.glob(os.path.join(data_path, dir, "*.jpg"))
        
        for image_path in image_paths:
            mask_save_path = os.path.join(
                data_path,
                dir,
                "mask",
                os.path.basename(image_path).split(".")[0] + "_mask.png",
            )
            ROI_save_path = os.path.join(
                data_path,
                dir,
                "ROI",
                os.path.basename(image_path).split(".")[0] + "_ROI.png",
            )

            start_time = time.time()
            print("start process image:" + image_path)
            process_image(image_path, mask_save_path, ROI_save_path, predictor)
            print(f"process image:{cnt} , cost time:{time.time() - start_time}s")
            cnt += 1


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    main()
