<template>
    <div class="table-container-wrapper">
        <el-button @click="fetchTableData">更新记录</el-button>
        <el-table :data="tableData" style="width: 100%">
            <el-table-column prop="date" label="时间戳" />
            <el-table-column prop="duration" label="耗时" />
            <el-table-column prop="uid" label="用户id" />
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="label" label="品种" />
            <el-table-column prop="level" label="等级" />
            <el-table-column prop="texture_level" label="纹理等级" />
            <el-table-column prop="coloration" label="着色度" />
            <el-table-column prop="defect_num" label="缺陷个数" />
            <el-table-column prop="defect_ratio" label="缺陷面积比" />
            <el-table-column prop="aspect_ratio" label="长宽比" />

        </el-table>
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
    flex-direction: row;
    margin: 20px;
}
</style>