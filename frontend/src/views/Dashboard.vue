<template>
    <div class="min-h-screen bg-gray-50 flex flex-col items-center pt-12">
        <div class="w-full max-w-6xl">
            <div class="bg-gradient-to-r from-blue-700 to-blue-500 rounded-2xl shadow-xl p-10 mb-12 flex flex-col items-center">
                <div class="flex items-center mb-4">
                    <span class="text-4xl mr-4 text-white">🧬</span>
                    <h1 class="text-3xl font-extrabold text-white tracking-widest">AI模型安全评估平台</h1>
                </div>
                <p class="text-lg text-blue-100 mb-2 text-center leading-relaxed">支持AI模型上传、对抗样本生成与安全性评估，助力AI安全研究与应用。</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <router-link to="/users" class="block rounded-xl shadow-lg p-6 bg-gradient-to-br from-cyan-100 to-blue-100 hover:from-cyan-200 hover:to-blue-200 transition transform hover:-translate-y-1">
                    <div class="text-lg font-bold mb-2 text-cyan-700">用户管理</div>
                    <div class="text-sm text-gray-600">组织、用户的分组与权限管理</div>
                </router-link>
                <router-link to="/models" class="block rounded-xl shadow-lg p-6 bg-gradient-to-br from-blue-100 to-blue-200 hover:from-blue-200 hover:to-blue-300 transition transform hover:-translate-y-1">
                    <div class="text-lg font-bold mb-2 text-blue-800">模型管理</div>
                    <div class="text-sm text-gray-600">上传、管理和评估AI模型</div>
                </router-link>
                <router-link to="/algorithms" class="block rounded-xl shadow-lg p-6 bg-gradient-to-br from-green-100 to-blue-100 hover:from-green-200 hover:to-blue-200 transition transform hover:-translate-y-1">
                    <div class="text-lg font-bold mb-2 text-green-800">算法管理</div>
                    <div class="text-sm text-gray-600">管理对抗样本生成算法</div>
                </router-link>
                <router-link to="/adversarial" class="block rounded-xl shadow-lg p-6 bg-gradient-to-br from-red-100 to-orange-100 hover:from-red-200 hover:to-orange-200 transition transform hover:-translate-y-1">
                    <div class="text-lg font-bold mb-2 text-red-700">对抗样本生成</div>
                    <div class="text-sm text-gray-600">生成对抗样本，评估模型安全性</div>
                </router-link>
                <router-link to="/file" class="block rounded-xl shadow-lg p-6 bg-gradient-to-br from-purple-100 to-blue-100 hover:from-purple-200 hover:to-blue-200 transition transform hover:-translate-y-1">
                    <div class="text-lg font-bold mb-2 text-purple-800">文件管理</div>
                    <div class="text-sm text-gray-600">上传、管理数据集和文件</div>
                </router-link>
                <router-link to="/samples" class="block rounded-xl shadow-lg p-6 bg-gradient-to-br from-yellow-100 to-blue-100 hover:from-yellow-200 hover:to-blue-200 transition transform hover:-translate-y-1">
                    <div class="text-lg font-bold mb-2 text-yellow-700">样本库</div>
                    <div class="text-sm text-gray-600">管理和增强样本集</div>
                </router-link>
                <router-link to="/inference" class="block rounded-xl shadow-lg p-6 bg-gradient-to-br from-pink-100 to-blue-100 hover:from-pink-200 hover:to-blue-200 transition transform hover:-translate-y-1">
                    <div class="text-lg font-bold mb-2 text-pink-700">推理服务</div>
                    <div class="text-sm text-gray-600">模型部署与在线推理</div>
                </router-link>
                <router-link to="/images" class="block rounded-xl shadow-lg p-6 bg-gradient-to-br from-indigo-100 to-blue-100 hover:from-indigo-200 hover:to-blue-200 transition transform hover:-translate-y-1">
                    <div class="text-lg font-bold mb-2 text-indigo-700">镜像管理</div>
                    <div class="text-sm text-gray-600">上传、管理和推送Docker镜像</div>
                </router-link>
            </div>
            
            <!-- 快速操作区域 -->
            <div class="mt-12">
                <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">快速操作</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-red-500">
                        <h3 class="text-lg font-semibold text-gray-800 mb-3">创建对抗样本任务</h3>
                        <p class="text-gray-600 text-sm mb-4">快速创建新的对抗样本生成任务，选择算法和目标模型</p>
                        <router-link to="/adversarial" class="inline-block bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition">
                            立即创建
                        </router-link>
                    </div>
                    <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
                        <h3 class="text-lg font-semibold text-gray-800 mb-3">上传AI模型</h3>
                        <p class="text-gray-600 text-sm mb-4">上传您的AI模型，准备进行安全性评估</p>
                        <router-link to="/models" class="inline-block bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition">
                            上传模型
                        </router-link>
                    </div>
                    <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
                        <h3 class="text-lg font-semibold text-gray-800 mb-3">管理算法</h3>
                        <p class="text-gray-600 text-sm mb-4">查看和管理可用的对抗攻击算法</p>
                        <router-link to="/algorithms" class="inline-block bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition">
                            查看算法
                        </router-link>
                    </div>
                </div>
            </div>
            
            <!-- 系统状态概览 -->
            <div class="mt-12">
                <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">系统状态</h2>
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div class="bg-white rounded-xl shadow-lg p-6 text-center">
                        <div class="text-3xl font-bold text-blue-600 mb-2">{{ systemStats.runningTasks }}</div>
                        <div class="text-gray-600">运行中任务</div>
                    </div>
                    <div class="bg-white rounded-xl shadow-lg p-6 text-center">
                        <div class="text-3xl font-bold text-green-600 mb-2">{{ systemStats.completedTasks }}</div>
                        <div class="text-gray-600">已完成任务</div>
                    </div>
                    <div class="bg-white rounded-xl shadow-lg p-6 text-center">
                        <div class="text-3xl font-bold text-purple-600 mb-2">{{ systemStats.availableAlgorithms }}</div>
                        <div class="text-gray-600">可用算法</div>
                    </div>
                    <div class="bg-white rounded-xl shadow-lg p-6 text-center">
                        <div class="text-3xl font-bold text-orange-600 mb-2">{{ systemStats.uploadedModels }}</div>
                        <div class="text-gray-600">已上传模型</div>
                    </div>
                </div>
            </div>
            
            <!-- 最近任务 -->
            <div class="mt-12">
                <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">最近任务</h2>
                <div class="bg-white rounded-xl shadow-lg p-6">
                    <div v-if="recentTasks.length === 0" class="text-center text-gray-500 py-8">
                        暂无最近任务
                    </div>
                    <div v-else class="space-y-4">
                        <div v-for="task in recentTasks" :key="task.id" class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                            <div class="flex items-center">
                                <div class="w-3 h-3 rounded-full mr-3" :class="getStatusColor(task.status)"></div>
                                <div>
                                    <div class="font-medium text-gray-800">{{ task.name }}</div>
                                    <div class="text-sm text-gray-500">{{ task.algorithm }} - {{ task.targetModel }}</div>
                                </div>
                            </div>
                            <div class="text-right">
                                <div class="text-sm text-gray-500">{{ task.createdAt }}</div>
                                <div class="text-xs text-gray-400">{{ task.status }}</div>
                            </div>
                        </div>
                    </div>
                    <div class="mt-4 text-center">
                        <router-link to="/adversarial" class="text-blue-600 hover:text-blue-800 text-sm">
                            查看所有任务 →
                        </router-link>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTaskStatistics, fetchAdversarialTasks } from '@/api.js'

// 系统统计数据
const systemStats = ref({
  runningTasks: 12,
  completedTasks: 156,
  availableAlgorithms: 8,
  uploadedModels: 24
})

// 最近任务
const recentTasks = ref([])

// 获取状态颜色
const getStatusColor = (status) => {
  const colorMap = {
    'running': 'bg-blue-500',
    'completed': 'bg-green-500',
    'failed': 'bg-red-500',
    'pending': 'bg-yellow-500',
    'paused': 'bg-gray-500'
  }
  return colorMap[status] || 'bg-gray-500'
}

// 加载系统统计数据
const loadSystemStats = async () => {
  try {
    const response = await getTaskStatistics()
    if (response.data && response.data.statistics) {
      systemStats.value = {
        runningTasks: response.data.statistics.runningTasks || 12,
        completedTasks: response.data.statistics.completedTasks || 156,
        availableAlgorithms: 8, // 默认值，后续可从API获取
        uploadedModels: 24 // 默认值，后续可从API获取
      }
    }
  } catch (error) {
    console.error('加载系统统计数据失败:', error)
  }
}

// 加载最近任务
const loadRecentTasks = async () => {
  try {
    const response = await fetchAdversarialTasks()
    if (response.data && response.data.tasks) {
      // 取最近5个任务
      recentTasks.value = response.data.tasks.slice(0, 5)
    }
  } catch (error) {
    console.error('加载最近任务失败:', error)
    // 使用模拟数据
    recentTasks.value = [
      {
        id: 1,
        name: 'FGSM对抗样本生成',
        algorithm: 'FGSM',
        targetModel: 'ResNet50',
        status: 'running',
        createdAt: '2024-01-15 10:30'
      },
      {
        id: 2,
        name: 'PGD攻击实验',
        algorithm: 'PGD',
        targetModel: 'VGG16',
        status: 'completed',
        createdAt: '2024-01-14 15:20'
      }
    ]
  }
}

onMounted(() => {
  loadSystemStats()
  loadRecentTasks()
})
</script>