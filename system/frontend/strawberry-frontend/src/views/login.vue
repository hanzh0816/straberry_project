<template>
    <div class="login-container">
        <h1>Login</h1>
        <!-- todo: 加入LOGO -->
        <el-input v-model="loginForm.username" placeholder="Username"></el-input>
        <el-input v-model="loginForm.password" placeholder="Password" show-password></el-input>
        <div class="button-container">
            <el-button type="primary" @click="login">Login</el-button>
            <Register></Register>
        </div>
        <el-divider></el-divider>
        <el-button type="text" @click="showForgotPasswordDialog">Forgot Password</el-button>


        <el-dialog title="Forgot Password" :visible.sync="forgotPasswordDialogVisible">
            <el-form>
                <el-form-item label="Username">
                    <el-input v-model="forgotPasswordForm.username" placeholder="Username"></el-input>
                </el-form-item>
            </el-form>
            <span slot="footer" class="dialog-footer">
                <el-button @click="forgotPasswordDialogVisible = false">Cancel</el-button>
                <el-button type="primary" @click="sendForgotPasswordEmail">Send Email</el-button>
            </span>
        </el-dialog>
    </div>
</template>
  
<script>
import axios from 'axios';
import Register from '../components/Register.vue';

export default {
    components: {
        Register,
    },
    data() {
        return {
            loginForm: {
                username: '',
                password: '',
            },
            forgotPasswordDialogVisible: false,
            forgotPasswordForm: {
                username: '',
            },
        };
    },
    methods: {
        login() {
            const { username, password } = this.loginForm;

            // this.$router.push('/index');

            axios.get('http://127.0.0.1:5000/users', {
                params: {
                    username,
                    password,
                },
            })
                .then(response => {
                    if (response.data.message == 'Login successful') {
                        const uid = response.data.uid;
                        localStorage.setItem("uid", uid);
                        this.$router.push('/index/imageshow');
                    }
                    else {
                        // 登录错误处理
                        // 根据后端返回的错误信息或状态码来显示相应的错误提示
                        // 例如：
                        if (response.data.message === 'Invalid username or password') {
                            alert('登录失败：用户名或密码错误');
                        } else {
                            alert('登录失败：未知错误');
                        }
                    }
                    // 清空输入框字段
                    this.loginForm.username = ''; // 清空用户名输入框
                    this.loginForm.password = ''; // 清空密码输入框
                })
                .catch(error => {
                    // todo: 处理登录失败后的逻辑
                    console.error(error);
                });
        },


        showForgotPasswordDialog() {
            this.forgotPasswordDialogVisible = true;
        },
        sendForgotPasswordEmail() {
            const { username } = this.forgotPasswordForm;
            axios.get('/api/forgot-password', {
                params: {
                    username,
                },
            })
                .then(response => {
                    // 处理发送找回密码邮件成功后的逻辑
                    console.log(response.data);
                    this.forgotPasswordDialogVisible = false;
                })
                .catch(error => {
                    // 处理发送找回密码邮件失败后的逻辑
                    console.error(error);
                });
        },
    },
};
</script>
  
<style>
.login-container {
    max-width: 300px;
    max-height: min-content;
    margin: 0 auto;
    padding: 20px;
}


.button-container {
    display: flex;
    /* 使用 Flex 布局 */
    justify-content: space-between;
    /* 左右对齐，按钮之间的空间平均分配 */
    max-width: 200px;
    /* 设置容器宽度，根据实际需要调整 */
}

.el-button {
    margin-top: 10px;
}

.dialog-footer {
    text-align: right;
}
</style>