<template>
    <div class="registWindow">
        <el-button type="primary" @click="registerDialogVisible = true">注册</el-button>

        <el-dialog title="注册" v-model="registerDialogVisible" width="30%">
            <el-form :model="registerForm" :rules="registerFormRules" ref="registerFormRules" label-width="auto"
                label-position="left" size="default">
                <el-form-item label="用户名" prop="username">
                    <el-input v-model="registerForm.username"></el-input>
                </el-form-item>

                <el-form-item label="密码" prop="password">
                    <el-input type="password" v-model="registerForm.password"></el-input>
                </el-form-item>

                <el-form-item label="手机号" prop="tele">
                    <el-input v-model="registerForm.tele"></el-input>
                </el-form-item>

                <el-form-item>
                    <el-button type="primary" @click="register">注册</el-button>
                    <el-button @click="cancelRegister">取消</el-button>
                </el-form-item>
            </el-form>
        </el-dialog>
    </div>
</template>
  
<script>

import axios from 'axios';
import { ElMessage } from 'element-plus';
export default {
    data() {
        return {
            registerDialogVisible: false,
            registerForm: {
                username: '',
                password: '',
                tele: ''
            },

            registerFormRules: {
                username: [
                    { required: true, message: '请输入用户名', trigger: 'blur' },
                ],
                password: [
                    { required: true, message: '请输入密码', trigger: 'blur' },
                    {
                        min: 3,
                        max: 18,
                        message: "长度在 3 到 18 个字符",
                        trigger: "blur",
                    }
                ],
                tele: [
                    { required: true, message: '请输入手机号', trigger: 'blur' },
                    {
                        min: 11,
                        max: 11,
                        message: "长度为11个字符",
                        trigger: "blur",
                    }
                ],
            },
        }
    },

    methods: {
        register() {
            // todo: 登录api实现
            // 登陆进行规则的校验，只有校验成功才能登陆,vaild=>所有的规则校验都成立才会进入到这里
            this.$refs.registerFormRules.validate((vaild) => {
                if (!vaild) {
                    ElMessage({
                        message: '请正确填写信息',
                        type: 'warning',
                        duration: 1500
                    })
                    console.log('error')
                    return;
                };

                const url = 'http://127.0.0.1:5000/users';
                const data = {};
                data['username'] = this.registerForm.username;
                data['password'] = this.registerForm.password;
                data['tele'] = this.registerForm.tele;

                axios.post(url, data)
                    .then(response => {
                        // 处理响应
                        if (response.status === 200) {
                            const returnData = response.data;
                            console.log(returnData);
                            console.log('数据发送成功');
                            this.registerForm.username = '';
                            this.registerForm.password = '';
                            this.registerForm.tele = '';
                            this.registerDialogVisible = false;

                            ElMessage({
                                message: '注册成功',
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
            });
        },
    },
}
</script> 