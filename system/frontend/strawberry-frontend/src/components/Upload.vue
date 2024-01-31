<template>
    <div>
        <el-button @click="selectImage">选择图片</el-button>
        <el-button @click="selectPoint">选择分割点</el-button>
        <el-button @click="updateImage">上传图片</el-button>
        <div class="image-container-wrapper">
            <div class="image-container">
                <el-image :src="selectedImage" alt="Selected Image" @click="handleImageClick" :style="selecteImageStyle" />
                <div v-if="selectedPoint" class="point"
                    :style="{ top: selectedPoint.y + 'px', left: selectedPoint.x + 'px' }">
                </div>
            </div>
            <div class="image-container">
                <el-image :src="segmentImage" alt="Segment Image" :style="segmentImageStyle" />

            </div>
        </div>
        <div v-if="selectedPoint">
            <p>已选择的点的坐标：</p>
            <p>x: {{ selectedPoint.x }}</p>
            <p>y: {{ selectedPoint.y }}</p>
        </div>
        <div> <el-table :data="tableData" style="width: 100%">
                <el-table-column prop="idx" label="指标" width="180" />
                <el-table-column prop="result" label="结果" />
            </el-table>
        </div>
    </div>
</template>
  
<script>
import { ref, reactive } from 'vue';
import axios from 'axios';
import { ElLoading } from 'element-plus'


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
                if (row.idx === '品种') {
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
        }
    }
};

</script>
  
<style scoped>
.image-container-wrapper {
    display: flex;
    flex-direction: row;
    margin: 20px;

    .image-container {
        padding: 30px 0;
        text-align: center;
        display: inline-block;
        /* width: 49%; */
        box-sizing: border-box;
        vertical-align: top;
        position: relative;
        width: 300px;
        height: 300px;
        margin: 20px;

        .el-image {
            padding: 0 5px;
            width: 300px;
            height: 300px;
            width: 100%;
            height: 200px;
        }

        .point {
            position: absolute;
            width: 10px;
            height: 10px;
            background-color: rgb(0, 0, 0);
            border-radius: 50%;
        }
    }


}
</style>