<template>
    <div class="index">
        <div class="head">
            <el-menu router :default-active="activeIndex" class="menu" mode="horizontal" @select="handleSelect">
                <el-menu-item index="/index/imageshow" style="font-size: 24px;">主页</el-menu-item>
                <el-menu-item index="/index/record" style="font-size: 24px;">记录</el-menu-item>
                <el-sub-menu>
                    <template #title><span class="menu-title" style="font-size: 24px;">我的</span></template>
                    <el-menu-item style="font-size: 18px;" @click="describedialogVisible = true">功能说明
                    </el-menu-item>
                    <el-menu-item style="font-size: 18px;" @click="exitLogin">退出登录
                    </el-menu-item>
                </el-sub-menu>
            </el-menu>
            <el-dialog v-model="describedialogVisible" title="功能说明" width="500">
                <p>
                    <br>本系统主要功能为识别草莓品种及其等级，使用方法: <br>
                    1. 点击“选择图片”按键，从本地文件中选择要识别的草莓图像 <br>
                    2. 点击“选择分割点”按键，之后鼠标左键点击图像中草莓区域 <br>
                    3. 点击“上传图片”按键对选择的区域进行分割及识别<br><br>
                    若重新识别按照上述方法重新操作，若识别完成则点击“上传记录”按键将草莓品种及其等级信息上传到草莓品种数据库中。<br><br>
                    点击上方“记录”按键即可跳转至操作记录显示页面<br><br>
                    退出点击“我的”->“退出登录”<br>
                </p>
                <template #footer>
                    <div class="dialog-footer">
                        <el-button type="primary" @click="describedialogVisible = false">关闭</el-button>
                    </div>
                </template>
            </el-dialog>
        </div>
        <div class="content">
            <router-view></router-view>
        </div>
    </div>
</template>
  
<script>

export default {
    data() {
        return {
            activeTab: 'strawberry',
            describedialogVisible: false,
        };
    },
    methods: {
        handleSelect(index) {
            this.activeTab = index;
        },



        exitLogin() {
            localStorage.removeItem('uid')
            this.$router.push('/')
        }
    }
};
</script>
  

<style>
.index {
    width: 100vw;
    height: 100vh;
}

.index .head .menu {
    background: #c2d5ff;
    height: 80px;

}
</style>