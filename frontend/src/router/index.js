import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import FileManager from '../views/FileManager.vue'
import ImageManager from '../views/ImageManager.vue'
import OrgManager from '../views/OrgManager.vue'
import ResourceManager from '../views/ResourceManager.vue'

const routes = [
    { path: '/login', component: Login },
    { path: '/dashboard', component: Dashboard },
    { path: '/files', component: FileManager },
    { path: '/images', component: ImageManager },
    { path: '/orgs', component: OrgManager },
    { path: '/resources', component: ResourceManager },
    { path: '/', redirect: '/login' }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router