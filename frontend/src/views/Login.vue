<template>
  <div class="auth-page">
    <el-card class="auth-card" shadow="always">
      <template #header>
        <h2>登录</h2>
        <p style="color:#909399;margin:0;font-size:14px">RAG 智能对话系统</p>
      </template>
      <el-form @submit.prevent="handleLogin" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="username" placeholder="请输入用户名" size="large" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" placeholder="请输入密码" size="large" show-password />
        </el-form-item>
        <el-button type="primary" size="large" :loading="loading" @click="handleLogin" style="width:100%">
          {{ loading ? '登录中...' : '登录' }}
        </el-button>
      </el-form>
      <div style="text-align:center;margin-top:16px;color:#909399;font-size:13px">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../api/index.js'
import { authStore } from '../stores/auth.js'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)

onMounted(() => { authStore.clearAuth() })

async function handleLogin() {
  if (!username.value || !password.value) { ElMessage.warning('请输入用户名和密码'); return }
  loading.value = true
  try {
    const res = await login(username.value, password.value)
    const d = res.data
    const token = d.data || d.token || d.access_token
    if (token) {
      authStore.setAuth({ username: username.value }, typeof token === 'string' ? token : '')
      router.push('/chat')
    } else { ElMessage.error('登录失败：' + (d.message || JSON.stringify(d))) }
  } catch (e) { if (!e.response) ElMessage.error('无法连接服务器，请确认后端已启动') }
  finally { loading.value = false }
}
</script>

<style scoped>
.auth-page { display: flex; justify-content: center; align-items: center; height: 100vh; background: #eef0f4; }
.auth-card { width: 400px; }
</style>
