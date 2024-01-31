import os
import glob
import time
from tkinter import NO
import cv2
import numpy as np
from segment_anything import sam_model_registry, SamPredictor


class SegmentTool(object):
    def __init__(self):
        self.predictor = self.sam_init()

    def segment(self, image, point):
        self.predictor.set_image(image)
        input_point = np.array([[point[0], point[1]]])
        input_label = np.array([1])

        masks, scores, _ = self.predictor.predict(
            point_coords=input_point,
            point_labels=input_label,
            multimask_output=True,
        )
        x, y, z = np.array(masks).shape
        threshold = 1e5
        pmask_idx = np.where(np.sum(np.reshape(masks, (x, y * z)), axis=1) > threshold)[
            0
        ]
        try:
            best_mask_idx = pmask_idx[np.argmax(scores[pmask_idx])]
            best_mask = masks[best_mask_idx]
            # print(np.array(best_mask).shape)
        except ValueError:
            best_mask = np.full((y, z), False, dtype=bool)

        best_mask = np.array(best_mask, dtype=np.uint8)
        ROI_image = cv2.bitwise_and(image, image, mask=best_mask)
        return ROI_image, best_mask

    @staticmethod
    def sam_init() -> SamPredictor:
        sam_checkpoint = "D://Files//checkpoints//SAM//sam_vit_b_01ec64.pth"
        device = "cuda"
        model_type = "vit_b"
        print("loading model")
        sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
        sam.to(device=device)
        predictor = SamPredictor(sam)
        print("loading model finished")

        return predictor
