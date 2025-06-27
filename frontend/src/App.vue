<template>
  <div class="min-h-screen bg-gray-100">
    <!-- 顶部导航条 -->
    <header class="w-full h-16 bg-gradient-to-r from-blue-900 to-blue-600 flex items-center px-8 shadow z-10">
      <div class="text-2xl font-bold text-white tracking-widest flex items-center">
        <span class="mr-3 w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center text-blue-200">🧬</span>
        AI模型安全评估平台
      </div>
      <div class="flex-1"></div>
      <!-- 右侧可预留用户信息/设置等 -->
    </header>
    <div class="flex">
      <!-- 侧边栏 -->
      <aside class="w-64 min-h-[calc(100vh-4rem)] bg-gradient-to-b from-blue-800 to-blue-700 shadow-lg flex-shrink-0 pt-8">
        <nav class="px-4">
          <div class="mb-6 text-blue-200 text-xs tracking-widest pl-2">功能导航</div>
          <ul class="space-y-4">
            <li>
              <router-link to="/dashboard" class="block py-3 px-6 rounded-xl text-lg font-medium transition hover:bg-blue-600 hover:text-white text-blue-100" active-class="bg-white text-blue-800 font-bold shadow">首页</router-link>
            </li>
            <li>
              <router-link to="/users" class="block py-3 px-6 rounded-xl text-lg font-medium transition hover:bg-blue-600 hover:text-white text-blue-100" active-class="bg-white text-blue-800 font-bold shadow">用户管理</router-link>
            </li>
            <li>
              <router-link to="/models" class="block py-3 px-6 rounded-xl text-lg font-medium transition hover:bg-blue-600 hover:text-white text-blue-100" active-class="bg-white text-blue-800 font-bold shadow">模型管理</router-link>
            </li>
            <li>
              <router-link to="/algorithms" class="block py-3 px-6 rounded-xl text-lg font-medium transition hover:bg-blue-600 hover:text-white text-blue-100" active-class="bg-white text-blue-800 font-bold shadow">算法管理</router-link>
            </li>
            <li>
              <router-link to="/file" class="block py-3 px-6 rounded-xl text-lg font-medium transition hover:bg-blue-600 hover:text-white text-blue-100" active-class="bg-white text-blue-800 font-bold shadow">文件管理</router-link>
            </li>
            <li>
              <router-link to="/samples" class="block py-3 px-6 rounded-xl text-lg font-medium transition hover:bg-blue-600 hover:text-white text-blue-100" active-class="bg-white text-blue-800 font-bold shadow">样本库</router-link>
            </li>
            <li>
              <router-link to="/inference" class="block py-3 px-6 rounded-xl text-lg font-medium transition hover:bg-blue-600 hover:text-white text-blue-100" active-class="bg-white text-blue-800 font-bold shadow">推理服务</router-link>
            </li>
          </ul>
        </nav>
      </aside>
      <!-- 主内容区 -->
      <main class="flex-1 min-h-[calc(100vh-4rem)] bg-gray-50">
        <router-view />
      </main>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const token = ref(localStorage.getItem('token'))
const username = computed(() => {
  // 可根据后端返回的用户信息调整
  return token.value ? '已登录' : ''
})
function logout() {
  localStorage.removeItem('token')
  token.value = null
  router.push('/login')
}
</script>
<style>
.router-link-exact-active {
  text-decoration: underline;
  font-weight: bold;
}
</style>