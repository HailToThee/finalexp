import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: null,
        user: null,
    }),
    actions: {
        async login(username, password) {
            try {
                const response = await axios.post('/api/auth/token', {
                    username,
                    password,
                })
                this.token = response.data.access_token
                localStorage.setItem('token', this.token)
                return true
            } catch (error) {
                console.error('Login failed:', error)
                return false
            }
        },
        logout() {
            this.token = null
            this.user = null
            localStorage.removeItem('token')
        },
    },
})