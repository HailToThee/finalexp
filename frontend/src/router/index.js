import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import ModelManagement from '../views/ModelManagement.vue'
import FileUploader from '../views/FileUploader.vue'
import AlgorithmManagement from '../views/AlgorithmManagement.vue'
import SampleLibrary from '../views/SampleLibrary.vue'
import InferenceService from '../views/InferenceService.vue'
import UserManagement from '../views/UserManagement.vue'
import ImageManagement from '../views/ImageManagement.vue'
import AlgorithmDetail from '../views/AlgorithmDetail.vue'
import AdversarialGeneration from '../views/AdversarialGeneration.vue'
import HyperParamTuning from '../views/HyperParamTuning.vue'
import AlgorithmTraining from '../views/AlgorithmTraining.vue'

const routes = [
    { path: '/', redirect: '/dashboard' },
    { path: '/login', component: Login },
    { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } },
    { path: '/models', component: ModelManagement, meta: { requiresAuth: true } },
    { path: '/file', component: FileUploader, meta: { requiresAuth: true } },
    { path: '/algorithms', component: AlgorithmManagement, meta: { requiresAuth: true } },
    { path: '/samples', component: SampleLibrary, meta: { requiresAuth: true } },
    { path: '/inference', component: InferenceService, meta: { requiresAuth: true } },
    { path: '/users', component: UserManagement, meta: { requiresAuth: true } },
    { path: '/images', component: ImageManagement, meta: { requiresAuth: true } },
    { path: '/algorithm/:id', component: AlgorithmDetail, meta: { requiresAuth: true } },
    { path: '/adversarial', component: AdversarialGeneration, meta: { requiresAuth: true } },
    { path: '/adversarial/tuning/:taskId', component: HyperParamTuning, meta: { requiresAuth: true } },
    { path: '/adversarial/training/:taskId', component: AlgorithmTraining, meta: { requiresAuth: true } },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    if (to.meta.requiresAuth && !token) {
        next('/login')
    } else if (to.path === '/login' && token) {
        next('/dashboard')
    } else {
        next()
    }
})

export default router