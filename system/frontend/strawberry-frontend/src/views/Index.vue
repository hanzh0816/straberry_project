<template>
    <div class="index">
        <div class="head">
            <el-menu router :default-active="activeIndex" class="menu" mode="horizontal" @select="handleSelect">
                <el-menu-item index="/index/imageshow">主页</el-menu-item>
                <el-menu-item index="/index/record">记录</el-menu-item>
                <el-sub-menu>
                    <template #title>我的</template>
                    <el-menu-item>功能说明</el-menu-item>
                    <el-menu-item>退出登录</el-menu-item>
                </el-sub-menu>
            </el-menu>
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
            activeTab: 'strawberry'
        };
    },
    methods: {
        handleSelect(index) {
            this.activeTab = index;
        }
    }
};
</script>
  

<style scoped >
.index {

    width: 100vw;
    height: 100vh;

    .head {
        width: 100vw;
        height: 100px;

        .menu {
            max-width: 100vw;
            height: 80px;
        }
    }
}
</style>