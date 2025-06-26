<template>
    <div class="min-h-screen flex items-center justify-center bg-gray-100">
        <div class="bg-white p-8 rounded shadow-md w-full max-w-md">
            <h2 class="text-2xl font-bold mb-6 text-center">Login</h2>
            <form @submit.prevent="handleLogin">
                <div class="mb-4">
                    <label class="block text-gray-600">Username</label>
                    <input v-model="username" type="text" class="w-full px-4 py-2 border rounded-md focus:outline-none" required />
                </div>
                <div class="mb-4">
                    <label class="block text-gray-600">Password</label>
                    <input v-model="password" type="password" class="w-full px-4 py-2 border rounded-md" required />
                </div>
                <button type="submit" class="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600">Login</button>
            </form>
            <p v-if="error">{{ error }}</p>
        </div>
    </div>
</template>
<script>
import axios from 'axios'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
    setup() {
        const store = useStore()
        const router = useRouter()
        const username = ref('')
        const password = ref('')
        const error = ref('')

        const handleLogin = async () => {
            try {
                const res = await axios.post('/api/auth/login', {
                    username: username.value,
                    password: password.value
                })
                store.commit('setToken', res.data.access_token)
                axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`
                router.push('/dashboard')
            } catch (e) {
                error.value = '用户名或密码错误'
            }
        }
        return { username, password, handleLogin, error }
    }
}
</script>