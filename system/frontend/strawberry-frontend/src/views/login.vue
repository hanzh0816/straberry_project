<template>
    <div class="login-wrapper">
        <el-container>
            <el-header>
                <el-container class="logo-container">
                    <el-aside width="200px">
                        <img class="logo" src="../assets/logo.png" alt="Logo" />
                    </el-aside>
                    <el-main class="title" style="font-size: 40px">登录</el-main>
                </el-container>
            </el-header>

            <el-main class="input">
                <div><el-input v-model="loginForm.username" placeholder="用户名"></el-input></div>
                <div><el-input v-model="loginForm.password" placeholder="密码" show-password></el-input></div>
            </el-main>
            <el-footer>
                <div><el-button type="primary" @click="login">登录</el-button></div>
                <div>
                    <Register></Register>
                </div>
                <div>
                    <ForgetPasswd></ForgetPasswd>
                </div>
            </el-footer>
        </el-container>
    </div>
</template>
  
<script>
import axios from 'axios';
import Register from '../components/Register.vue';
import ForgetPasswd from '../components/ForgetPasswd.vue';

export default {
    components: {
        Register,
        ForgetPasswd,
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
.login-wrapper {
    display: flex;
    width: 320px;
    align-items: center;
    border-radius: 10px;
    background-color: #fff;
    box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.12), 0 0 6px 0 rgba(0, 0, 0, 0.04);

    .el-header {
        margin: 10 auto;
        height: 100px;
        justify-content: space-between;

        .logo-container {
            .el-aside {
                width: 120px;
                height: 120px;
                justify-content: left;
            }

            .title {
                display: flex;
                height: 120px;
                text-align: left;
            }

        }
    }

    .input {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        width: 320px;
        height: 220px;

        .el-input {
            width: 280px;
            height: 40px;
            margin-bottom: 20px;
        }
    }


    .el-footer {
        width: 300px;
        display: flex;
        justify-content: space-around;
        align-items: center
    }

}
</style>