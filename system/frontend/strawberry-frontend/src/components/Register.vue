<template>
    <div>
        <el-button type="primary" @click="registerDialogVisible = true">注册</el-button>

        <el-dialog title="注册" v-model="registerDialogVisible" width="30%">
            <el-form :model="registerForm" :rules="registerFormRules" ref="registerFormRules">
                <el-form-item label="用户名" prop="username">
                    <el-input v-model="registerForm.username"></el-input>
                </el-form-item>

                <el-form-item label="密码" prop="password">
                    <el-input type="password" v-model="registerForm.password"></el-input>
                </el-form-item> 

                <el-form-item label="手机号" prop="phone">
                    <el-input v-model="registerForm.phone"></el-input>
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

export default {
    data() {
        return {
            registerDialogVisible: false,
            registerForm: {
                username: '',
                password: '',
                phone: ''
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
                phone: [
                    { required: true, message: '请输入手机号', trigger: 'blur' },
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
                    console.log('error')
                    return;
                };
                // 请求数据，格式是formdata，需要添加 this.qs.stringify()进行格式转换
                this.$axios.post("http://192.168.17.176:8089/register", this.qs.stringify(this.loginRuleForm)).then(
                    (res) => {
                        console.log(res)

                        if (res.data.code != 0 && res.data.code != 401) {
                            return this.$message.error(res.data.msg);
                        }
                    })
            });
        },
    },
}
</script> 