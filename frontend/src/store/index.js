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
        async register(username, password) {
            try {
                const response = await axios.post('/api/auth/register', null, {
                    params: { username, password }
                })
                return { success: true, msg: response.data.msg }
            } catch (error) {
                let msg = '注册失败'
                if (error.response && error.response.data && error.response.data.detail) {
                    msg = error.response.data.detail
                } else if (error.message) {
                    msg = error.message
                }
                return { success: false, msg }
            }
        },
        logout() {
            this.token = null
            this.user = null
            localStorage.removeItem('token')
        },
    },
})