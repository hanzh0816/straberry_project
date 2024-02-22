<template>
    <div class="forgetPasswdWindow">
        <el-button type="primary" @click="forgetPasswdDialogVisible = true">忘记密码</el-button>

        <el-dialog title="忘记密码" v-model="forgetPasswdDialogVisible" width="30%">
            <el-form :model="forgetPasswdForm" :rules="forgetPasswdFormRules" ref="forgetPasswdFormRules" label-width="auto"
                label-position="left" size="default">
                <el-form-item label="用户名" prop="username">
                    <el-input v-model="forgetPasswdForm.username"></el-input>
                </el-form-item>

                <el-form-item label="手机号" prop="tele">
                    <el-input v-model="forgetPasswdForm.tele"></el-input>
                </el-form-item>

                <el-form-item label="新密码" prop="password">
                    <el-input type="password" v-model="forgetPasswdForm.password"></el-input>
                </el-form-item>



                <el-form-item>
                    <el-button type="primary" @click="updatePasswd">更新密码</el-button>
                    <el-button @click="cancelUpdatePasswd">取消</el-button>
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
            forgetPasswdDialogVisible: false,
            forgetPasswdForm: {
                username: '',
                password: '',
                tele: ''
            },

            forgetPasswdFormRules: {
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
        updatePasswd() {
            this.$refs.forgetPasswdFormRules.validate((valid) => {
                if (!valid) {
                    ElMessage({
                        message: '请正确填写信息',
                        type: 'warning',
                        duration: 1500
                    })
                    console.log('error')
                    return;
                };
                const username = this.forgetPasswdForm.username
                const newPassword = this.forgetPasswdForm.password
                const tele = this.forgetPasswdForm.tele
                // check phone number
                axios.get('http://127.0.0.1:5000/check', {
                    params: {
                        username,
                        tele,
                        newPassword,
                    },
                }).then(response => {
                    if (response.data.message == 'success') {
                        ElMessage({
                            message: '密码更新成功',
                            type: 'success',
                            duration: 2000
                        })
                        // 清空输入框字段
                        this.forgetPasswdForm.username = '';
                        this.forgetPasswdForm.password = '';
                        this.forgetPasswdForm.tele = '';
                        this.forgetPasswdDialogVisible = false;
                    }
                    else {
                        ElMessage({
                            message: '用户名或手机号错误',
                            type: 'warning',
                            duration: 3000
                        })
                    }
                    // 清空输入框字段
                    this.forgetPasswdForm.username = '';
                    this.forgetPasswdForm.password = '';
                    this.forgetPasswdForm.tele = '';
                })
                    .catch(error => {
                        console.error(error);
                    });

            })

        },
        cancelUpdatePasswd() {
            // 清空输入框字段
            this.forgetPasswdForm.username = '';
            this.forgetPasswdForm.password = '';
            this.forgetPasswdForm.tele = '';
            this.forgetPasswdDialogVisible = false;
        },


    },
}
</script>