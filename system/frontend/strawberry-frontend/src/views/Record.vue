<template>
    <div class="table-container-wrapper">
        <div class="table-container">
            <div class='record-table'>
                <el-table :data="tableData" style="width: 100%; border-radius: 5px;  border: 1px solid #ccc;">
                    <el-table-column prop="timestamp" label="时间戳" align="center" width="180" />
                    <el-table-column prop="duration" label="耗时" align="center" />
                    <el-table-column prop="uid" label="用户id" align="center" />
                    <el-table-column prop="username" label="用户名" align="center" />
                    <el-table-column prop="label" label="品种" align="center" />
                    <el-table-column prop="level" label="等级" align="center" />
                    <el-table-column prop="texture_level" label="纹理等级" align="center" />
                    <el-table-column prop="coloration" label="着色度" align="center" />
                    <el-table-column prop="defect_num" label="缺陷个数" align="center" />
                    <el-table-column prop="defect_ratio" label="缺陷面积比" align="center" />
                    <el-table-column prop="aspect_ratio" label="长宽比" align="center" />
                </el-table>
                <div class="record-button">
                    <el-button @click="fetchTableData" type="primary">更新记录</el-button>
                </div>
            </div>
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
            tableData: [

            ]
        };
    },
    methods: {
        fetchTableData() {
            // 使用适当的方法从后端获取数据并将其赋值给tableData
            // 以下示例为使用axios发送GET请求
            axios
                .get('http://127.0.0.1:5000/update')
                .then(response => {
                    const data = response.data;
                    this.tableData = data;
                })
                .catch(error => {
                    console.error(error);
                });
        }
    }
};
</script>
   
<style>
.table-container-wrapper {
    display: flex;
    margin: 20px;
    justify-content: center;

    .table-container {
        width: 80%;
        padding: 20px;
        margin: 20px;
        display: flex;
        justify-content: center;
        align-items: center;

        .record-table {
            max-width: 80%;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;

            .record-button {
                margin-top: 30px;

            }
        }



    }
}
</style>