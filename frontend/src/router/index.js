import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import ModelManagement from '../views/ModelManagement.vue'
import FileUploader from '../views/FileUploader.vue'
import AlgorithmManagement from '../views/AlgorithmManagement.vue'
import SampleLibrary from '../views/SampleLibrary.vue'
import InferenceService from '../views/InferenceService.vue'
import UserManagement from '../views/UserManagement.vue'
const routes = [
    { path: '/', redirect: '/dashboard' },
    { path: '/login', component: Login },
    { path: '/dashboard', component: Dashboard },
    { path: '/models', component: ModelManagement },
    { path: '/file', component: FileUploader },
    { path: '/algorithms', component: AlgorithmManagement },
    { path: '/samples', component: SampleLibrary },
    { path: '/inference', component: InferenceService },
    { path: '/users', component: UserManagement },
]
const router = createRouter({
    history: createWebHistory(),
    routes,
})
// router.beforeEach((to, from, next) => {
//     const token = localStorage.getItem('token')
//     if (to.meta.requiresAuth && !token) {
//         next('/login')
//     } else {
//         next()
//     }
// })
export default router