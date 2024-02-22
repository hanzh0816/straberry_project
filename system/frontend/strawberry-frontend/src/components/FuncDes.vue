<template>
    <el-dialog v-model="describedialogVisible" title="功能说明" width="500">
        <span>
            本系统主要功能为识别草莓品种及其等级，使用方法：
            1. 点击“选择图片”按键，从本地文件中选择要识别的草莓图像
            2. 点击“选择分割点”按键，之后鼠标左键点击图像中草莓区域
            3. 点击“上传图片”按键对选择的区域进行分割及识别

            若重新识别按照上述方法重新操作，若识别完成则点击“上传记录”按键将草莓品种及其等级信息上传到草莓品种数据库中。

            点击上方“记录”按键即可跳转至操作记录显示页面

            退出点击“我的”->“退出登录”

        </span>
        <template #footer>
            <div class="dialog-footer">
                <el-button type="primary" @click="describedialogVisible = false">关闭</el-button>
            </div>
        </template>
    </el-dialog>
</template>
  
<script lang="ts" setup>
import { ref } from 'vue'

const describedialogVisible = ref(false)

</script>
  