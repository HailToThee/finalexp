<template>
    <div class="min-h-screen flex items-center justify-center bg-gray-100">
        <div class="bg-white p-8 rounded shadow-md w-full max-w-md">
            <h2 class="text-2xl font-bold mb-6 text-center">登录</h2>
            <form @submit.prevent="handleLogin">
                <div class="mb-4">
                    <label class="block text-gray-600">用户名</label>
                    <input v-model="username" type="text" class="w-full px-4 py-2 border rounded-md focus:outline-none" required />
                </div>
                <div class="mb-4">
                    <label class="block text-gray-600">密码</label>
                    <input v-model="password" type="password" class="w-full px-4 py-2 border rounded-md" required />
                </div>
                <button type="submit" class="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600" :disabled="loading">
                    {{ loading ? '登录中...' : '登录' }}
                </button>
                <div v-if="error" class="text-red-500 text-center mt-4">{{ error }}</div>
            </form>
            <div class="text-center mt-4">
                <button @click="showRegister = true" class="text-blue-500 hover:underline">没有账号？注册</button>
            </div>
        </div>
        <div v-if="showRegister" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
            <div class="bg-white p-8 rounded shadow-md w-full max-w-md relative">
                <button @click="showRegister = false" class="absolute top-2 right-2 text-gray-400 hover:text-gray-600">×</button>
                <h2 class="text-2xl font-bold mb-6 text-center">注册</h2>
                <form @submit.prevent="handleRegister">
                    <div class="mb-4">
                        <label class="block text-gray-600">用户名</label>
                        <input v-model="regUsername" type="text" class="w-full px-4 py-2 border rounded-md focus:outline-none" required />
                    </div>
                    <div class="mb-4">
                        <label class="block text-gray-600">密码</label>
                        <input v-model="regPassword" type="password" class="w-full px-4 py-2 border rounded-md" required />
                    </div>
                    <button type="submit" class="w-full bg-green-500 text-white py-2 rounded-md hover:bg-green-600" :disabled="regLoading">
                        {{ regLoading ? '注册中...' : '注册' }}
                    </button>
                    <div v-if="regMsg" :class="{'text-green-500': regSuccess, 'text-red-500': !regSuccess}" class="text-center mt-4">{{ regMsg }}</div>
                </form>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/index'
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const router = useRouter()
const store = useAuthStore()
const showRegister = ref(false)
const regUsername = ref('')
const regPassword = ref('')
const regLoading = ref(false)
const regMsg = ref('')
const regSuccess = ref(false)
async function handleLogin() {
    loading.value = true
    error.value = ''
    const success = await store.login(username.value, password.value)
    loading.value = false
    if (success) {
        router.push('/dashboard')
    } else {
        error.value = '用户名或密码错误'
    }
}
async function handleRegister() {
    regLoading.value = true
    regMsg.value = ''
    regSuccess.value = false
    const res = await store.register(regUsername.value, regPassword.value)
    regLoading.value = false
    regMsg.value = res.msg
    regSuccess.value = res.success
    if (res.success) {
        setTimeout(() => {
            showRegister.value = false
            username.value = regUsername.value
            password.value = regPassword.value
            regUsername.value = ''
            regPassword.value = ''
            regMsg.value = ''
        }, 1200)
    }
}
</script>