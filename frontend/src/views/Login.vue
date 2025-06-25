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
        </div>
    </div>
</template>
<script>
import { useAuthStore } from '../store/auth'
export default {
    data() {
        return {
            username: '',
            password: '',
        }
    },
    methods: {
        async handleLogin() {
            const store = useAuthStore()
            const success = await store.login(this.username, this.password)
            if (success) {
                this.$router.push('/dashboard')
            } else {
                alert('Login failed')
            }
            }
        },
    }
</script>