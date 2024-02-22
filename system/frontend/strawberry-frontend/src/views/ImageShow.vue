<template>
    <div class="imageshow">
        <div class="image-container">
            <div class="row1">
                <div class="select-image">
                    <div>选择草莓图像：</div>
                    <div class="select-image-inner" style="position: relative;">
                        <el-image :src="selectedImage" alt="Selected Image" @click="handleImageClick"
                            :style="selecteImageStyle">
                        </el-image>
                        <div v-if="selectedPoint" class="point"
                            :style="{ top: selectedPoint.y + 'px', left: selectedPoint.x + 'px' }">
                        </div>
                    </div>


                </div>

                <div class="segement-image">
                    <div>分割图像：</div>
                    <el-image :src="segmentImage" alt="Segment Image" :style="segmentImageStyle" />
                </div>
            </div>

            <div class="row2">
                <div class="text-container">
                    <div class="select-point">
                        <div class="label">分割点坐标：<div v-if="selectedPoint" class="content">{{ selectedPoint.x }}，{{
                            selectedPoint.y }}</div>
                        </div>

                    </div>
                </div>
                <div class="buttons-container">
                    <el-button type="primary" @click="selectImage">选择图片</el-button>
                    <el-button type="primary" @click="selectPoint">选择分割点</el-button>
                    <el-button type="primary" @click="updateImage">上传图片</el-button>
                </div>
            </div>
        </div>

        <div class="table-container">

            <div>选择草莓图像：</div>
            <el-table class="table" :data="tableData" border stripe
                style="width: 100%; border-radius: 5px; max-width: 500px; border: 1px solid #ccc;">
                <el-table-column prop="idx" label="指标" width="180" align="center" />
                <el-table-column prop="result" label="结果" align="center" />
            </el-table>

            <div class="update-button-container">
                <el-button class="update-button" type="primary" @click="updateRecord">上传记录</el-button>
            </div>

        </div>

    </div>
</template>
  
<script>
import { ref, reactive } from 'vue';
import axios from 'axios';
import { ElLoading,ElMessage } from 'element-plus'


export default {
    data() {
        return {
            selectedImage: '',
            segmentImage: '',
            selectedPoint: null,
            selectingPoint: false,
            realPoint: null,
            scale_ratio: null,
            imageWidth: 300, // 图像容器的宽度
            imageHeight: 300, // 图像容器的高度

            tableData: [
                { idx: '耗时', result: '' },
                { idx: '品种', result: '' },
                { idx: '等级', result: '' },
                { idx: '纹理等级', result: '' },
                { idx: '着色度', result: '' },
                { idx: '缺陷个数', result: '' },
                { idx: '缺陷面积比', result: '' },
                { idx: '长宽比', result: '' }
            ]
        };
    },
    computed: {
        selecteImageStyle() {
            if (this.selectedImage) {
                const image = new Image();
                image.src = this.selectedImage;
                const imageAspectRatio = image.width / image.height;
                const aspectRatio = this.imageWidth / this.imageHeight;
                let width = this.imageWidth;
                let height = this.imageHeight;
                if (imageAspectRatio < aspectRatio) { // 统一长宽比
                    height = this.imageWidth / imageAspectRatio;
                } else {
                    width = this.imageHeight * imageAspectRatio;
                }
                this.scale_ratio = width / image.width;
                return {
                    width: `${width}px`,
                    height: `${height}px`
                };
            }
            return null;
        },
        segmentImageStyle() {
            if (this.segmentImage) {
                const image = new Image();
                image.src = this.segmentImage;
                const imageAspectRatio = image.width / image.height;
                const aspectRatio = this.imageWidth / this.imageHeight;
                let width = this.imageWidth;
                let height = this.imageHeight;
                if (imageAspectRatio < aspectRatio) { // 统一长宽比
                    height = this.imageWidth / imageAspectRatio;
                } else {
                    width = this.imageHeight * imageAspectRatio;
                }
                return {
                    width: `${width}px`,
                    height: `${height}px`
                };
            }
            return null;
        }
    },
    methods: {

        updateTable(returnData) {
            this.tableData.forEach(row => {
                if (row.idx === '耗时') {
                    row.result = returnData.duration;
                }
                else if (row.idx === '品种') {
                    row.result = returnData.label;
                } else if (row.idx === '等级') {
                    row.result = returnData.level;
                } else if (row.idx === '纹理等级') {
                    row.result = returnData.texture_level;
                } else if (row.idx === '着色度') {
                    const percentage = (returnData.coloration * 100).toFixed(2) + '%'
                    row.result = percentage;
                } else if (row.idx === '缺陷个数') {
                    row.result = returnData.defect_num;
                } else if (row.idx === '缺陷面积比') {
                    const percentage = (returnData.defect_ratio * 100).toFixed(2) + '%'
                    row.result = percentage;
                } else if (row.idx === '长宽比') {
                    row.result = returnData.aspect_ratio.toFixed(2);
                }
            });
        },

        selectImage() {
            this.selectedImage = '';
            this.selectedPoint = null;
            this.selectingPoint = false;
            // 通过 input[type="file"] 元素选择图片
            const inputElement = document.createElement('input');
            inputElement.type = 'file';
            inputElement.accept = 'image/*';
            inputElement.addEventListener('change', (event) => {
                const file = event.target.files[0];
                const reader = new FileReader();
                reader.onload = (e) => {
                    this.selectedImage = e.target.result;
                };
                reader.readAsDataURL(file);
            });
            inputElement.click();
        },
        selectPoint() {
            this.selectingPoint = true;
        },
        handleImageClick(event) {

            if (this.selectingPoint) {

                const image = new Image();
                image.src = this.selectedImage;
                const imageAspectRatio = image.width / image.height;
                const aspectRatio = this.imageWidth / this.imageHeight;
                let width = this.imageWidth;
                let height = this.imageHeight;
                if (imageAspectRatio < aspectRatio) { // 统一长宽比
                    height = this.imageWidth / imageAspectRatio;
                } else {
                    width = this.imageHeight * imageAspectRatio;
                }
                this.scale_ratio = width / image.width;

                const x = event.offsetX;
                const y = event.offsetY;
                this.selectedPoint = { x, y };
                const real_x = Math.ceil(x / this.scale_ratio)
                const real_y = Math.ceil(y / this.scale_ratio)
                this.realPoint = { real_x, real_y };
                this.selectingPoint = false;
            }
        },

        updateImage() {
            const loadingInstance = ElLoading.service({ text: '计算中' })
            const url = 'http://127.0.0.1:5000/handle'; // 替换成实际的后端接口地址
            const imageData = this.selectedImage.replace(/^data:image\/\w+;base64,/, '');
            const realPoint = this.realPoint;
            // 创建一个 FormData 对象，用于存储要发送的数据
            const formData = new FormData();
            formData.append('image', imageData);
            formData.append('real_x', realPoint.real_x);
            formData.append('real_y', realPoint.real_y);

            axios.post(url, formData)
                .then(response => {
                    // 处理响应
                    loadingInstance.close()
                    if (response.status === 200) {
                        const returnData = response.data;
                        const base64Image = returnData.image;
                        this.segmentImage = 'data:image/png;base64,' + base64Image;
                        this.updateTable(returnData);

                        console.log('数据发送成功');
                    } else {
                        // 请求失败
                        console.error('数据发送失败');
                    }
                })
                .catch(error => {
                    // 捕获异常
                    console.error('发生错误:', error);
                });
        },

        updateRecord() {
            const url = 'http://127.0.0.1:5000/update'; // 替换成实际的后端接口地址
            const data = {};

            const uid = localStorage.getItem('uid');
            data['uid'] = uid;

            this.tableData.forEach(row => {
                if (row.idx === '耗时') {
                    data['duration'] = row.result;
                } else if (row.idx === '品种') {
                    data['label'] = row.result;
                } else if (row.idx === '等级') {
                    data['level'] = row.result;
                } else if (row.idx === '纹理等级') {
                    data['texture_level'] = row.result;
                } else if (row.idx === '着色度') {
                    data['coloration'] = row.result;
                } else if (row.idx === '缺陷个数') {
                    data['defect_num'] = row.result;
                } else if (row.idx === '缺陷面积比') {
                    data['defect_ratio'] = row.result;
                } else if (row.idx === '长宽比') {
                    data['aspect_ratio'] = row.result;
                }
            });

            axios.post(url, data)
                .then(response => {
                    // 处理响应
                    if (response.status === 200) {

                        console.log('数据发送成功');
                        ElMessage({
                        message: '记录上传成功',
                        type: 'success',
                        duration: 1500
                    })
                    } else {
                        // 请求失败
                        console.error('数据发送失败');
                    }
                })
                .catch(error => {
                    // 捕获异常
                    console.error('发生错误:', error);
                });

        }
    }
};

</script>
  
<style scoped>
.imageshow {
    display: flex;
    margin: 20px;
    /* align-items: center; */
    height: 80vh;
    width: 100vw;
}

.image-container {

    /* align-items: center; */
    padding-left: 90px;
    justify-content: space-between;
    flex-basis: 50%;
    display: flex;

    flex-direction: column;

    .row1 {
        flex-basis: 50%;
        display: flex;

        .select-image {
            flex-basis: 50%;

            .select-image-inner {
                width: 300px;
                height: 300px;
            }
        }

        .segement-image {
            flex-basis: 50%;
        }
    }

    .row2 {
        flex-basis: 50%;
        height: 100px;
        display: flex;

        /* align-items: center; */

        .text-container {
            flex-basis: 50%;
            align-items: center;

            .select-point {
                width: 300px;
                height: 70px;
                border: 3px solid #50505067;

                border-radius: 10px;
                /* 边框样式 */
                padding: 10px;
                /* 内边距 */
            }
        }

        .button-container {
            flex-basis: 50%;
            align-items: center;
        }



    }
}

.table-container {
    flex-basis: 50%;
    display: flex;
    flex-direction: column;

    .table {
        display: flex;
    }

    .update-button-container {

        display: flex;
        width:400px;
        margin-top: 10px;
        justify-content: center;
        align-items: center;
        .update-button {
            display: flex;
            margin-top: 10px;
            width: 80px;
        }
    }



}

.el-image {
    width: 300px;
    height: 300px;
}

.el-button {
    height: 40px;
}

.point {
    position: absolute;
    width: 10px;
    height: 10px;
    background-color: rgb(0, 0, 0);
    border-radius: 50%;
}
</style>