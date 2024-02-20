import io
import os
import sys
import numpy as np
import base64
import cv2
import time
from datetime import datetime
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
WIN = sys.platform.startswith("win")
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = "sqlite:///"
else:  # 否则使用四个斜线
    prefix = "sqlite:////"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = prefix + os.path.join(app.root_path, "data.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db.init_app(app)

cors.init_app(app)


class UserAPI(MethodView):
    def get(self):
        username = request.args.get("username")
        password = request.args.get("password")
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            return {"message": "Login successful", "uid": user.uid}
        else:
            return {"message": "Invalid username or password"}

    def post(self):
        form = request.json
        print(form)
        user = User()
        uid = len(User.query.all()) + 1
        user.uid = uid
        user.username = form["username"]
        user.password = form["password"]
        user.tele = form["tele"]
        print(user)
        db.session.add(user)
        db.session.commit()
        return {
            "status": "success",
            "message": "数据加载成功",
            "uid": uid,
            "username": form["username"],
            "password": form["password"],
        }


class RecordAPI(MethodView):
    def get(self):
        records = Record.query.all()
        # 将记录中的 timestamp 属性转换为字符串
        formatted_records = []
        for record in records:
            uid = record.uid
            user = User.query.filter_by(uid=uid).first()
            username = user.username
            formatted_record = {
                "timestamp": record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": record.duration,
                "uid": record.uid,
                "username": username,
                "label": record.label,
                "level": record.level,
                "texture_level": record.texture_level,
                "coloration": record.coloration,
                "defect_num": record.defect_num,
                "defect_ratio": record.defect_ratio,
                "aspect_ratio": record.aspect_ratio,
            }
            formatted_records.append(formatted_record)
        return jsonify(formatted_records)

    def post(self):
        form = request.json
        print(form)
        record = Record()
        record.timestamp = datetime.now()
        record.uid = int(form["uid"])
        record.duration = form["duration"]
        record.label = form["label"]
        record.level = form["level"]
        record.texture_level = form["texture_level"]
        record.coloration = form["coloration"]
        record.defect_num = form["defect_num"]
        record.defect_ratio = form["defect_ratio"]
        record.aspect_ratio = form["aspect_ratio"]

        db.session.add(record)
        db.session.commit()
        return {"status": "success", "message": "数据加载成功"}


@app.route("/handle", methods=["POST"])
def handle():
    # 获取请求中的数据
    selected_image = request.form["image"]
    real_x = request.form["real_x"]
    real_y = request.form["real_y"]

    # base64解码
    image_data = base64.b64decode(selected_image)
    image = Image.open(io.BytesIO(image_data))
    image = np.array(image)  # image: RGB格式

    begin_time = time.time()
    # 分割图像
    start_time = time.time()
    ROI_image, best_mask = segment_predictor.segment(
        image, (real_x, real_y)
    )  # ROI_image: RGB格式
    print(f"segment time : {time.time() - start_time}")

    # 分类
    start_time = time.time()
    label = predict_image(ROI_image)
    print(f"label time : {time.time() - start_time}")

    # 分级
    start_time = time.time()
    (level, texture_level, coloration, defect_num, defect_ratio, aspect_ratio) = (
        decide_tree_level(ROI_image, best_mask)
    )
    print(f"level time : {time.time() - start_time}")

    # cv2的encode 通道顺序是BGR, 所以要转成BGR格式以encode
    ROI_image = cv2.cvtColor(ROI_image, cv2.COLOR_RGB2BGR)
    image_bytes = cv2.imencode(".jpg", ROI_image)[1].tobytes()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    end_time = time.time()
    total_time = int(end_time - start_time)

    return_data = {}
    return_data["duration"] = total_time
    return_data["image"] = base64_image
    return_data["label"] = label  # 类别标签
    return_data["level"] = level  # 分级
    return_data["texture_level"] = texture_level  # 纹理等级 1为细腻，3为粗糙
    return_data["coloration"] = coloration  # 着色度
    return_data["defect_num"] = defect_num  # 缺陷个数
    return_data["defect_ratio"] = defect_ratio  # 缺陷面积比
    return_data["aspect_ratio"] = aspect_ratio  #

    # 返回响应
    return jsonify(return_data)


@app.route("/check", methods=["GET"])
def check_phone_num():
    username = request.args.get("username")
    tele = request.args.get("tele")
    newPassword = request.args.get("newPassword")
    user = User.query.filter_by(username=username, tele=tele).first()
    if user:
        user.password = newPassword
        db.session.commit()
        return {"check": True, "uid": user.uid}
    else:
        return {"message": "Invalid username or phone number"}


@app.cli.command()
def forge():
    db.drop_all()
    db.create_all()
    User._init_db()
    Record._init_db()


user_view = UserAPI.as_view("user_api")
app.add_url_rule("/users", view_func=user_view, methods=["GET", "POST"])

record_view = RecordAPI.as_view("record_api")
app.add_url_rule("/update", view_func=record_view, methods=["GET", "POST"])

if __name__ == "__main__":
    app.run()
