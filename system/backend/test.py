import io
import os
import sys
import numpy as np
import base64
import cv2
import matplotlib.pyplot as plt
from PIL import Image
from flask import Flask, request, jsonify
from flask.views import MethodView
from extension import db
from extension import cors

from models import User, Record

from methods import SegmentTool

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from cls import predict_image
from rating import decide_tree_level


segment_predictor = SegmentTool()

if __name__ == "__main__":
    image = cv2.imread(r"C:\Users\hanzh\Desktop\HY_1_ROI.png")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    ROI_image, best_mask = segment_predictor.segment(
        image, (1320, 1610)
    )  # ROI_image: RGB格式

    # 分类
    label = predict_image(ROI_image)
    # 分级

    print(decide_tree_level(ROI_image, best_mask))
