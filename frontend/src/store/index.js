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
                const params = new URLSearchParams();
                params.append('username', username);
                params.append('password', password);
                
                const response = await axios.post('/api/auth/token', params, {
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
                })
                this.token = response.data.access_token
                this.user = response.data.user_info
                localStorage.setItem('token', this.token)
                return true
            } catch (error) {
                console.error('Login failed:', error)
                return false
            }
        },
        async register(username, password, nickname, department, phone, email, gender, position, remark) {
            try {
                const response = await axios.post('/api/auth/register', {
                    username,
                    password,
                    nickname,
                    department,
                    phone,
                    email,
                    gender,
                    position,
                    remark
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