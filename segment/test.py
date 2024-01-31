from copy import deepcopy
from typing import List
import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
from utils import *
from segment_anything import sam_model_registry, SamPredictor

os.chdir(os.path.dirname(__file__))

if __name__ == "__main__":

    sam_checkpoint = "D://Files//checkpoints//SAM//sam_vit_b_01ec64.pth"
    device = "cuda"
    model_type = "vit_b"
    print("loading model")

    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
    sam.to(device=device)
    predictor = SamPredictor(sam)
    print("loading model finished")

    image = cv2.imread(r"D:\Files\data\Strawberry Pictures\NY\NY_302.jpg")
    reddest_point = find_reddest_pixel(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    predictor.set_image(image)

    # input_point = np.array([[reddest_point[0], reddest_point[1]]])
    input_point = np.array([[1626, 1416]])
   
    input_label = np.array([1])

    plt.figure(figsize=(10, 10))
    plt.imshow(image)
    show_points(input_point, input_label, plt.gca())
    plt.axis("on")


    print("predicting mask")
    masks, scores, logits = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=False,
    )

    save_mask(masks, "1.png")