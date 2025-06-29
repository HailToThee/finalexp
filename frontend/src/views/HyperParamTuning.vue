<template>
  <div class="p-8 bg-gray-50 min-h-screen">
    <div class="max-w-7xl mx-auto">
      <!-- 页面标题 -->
      <div class="bg-white rounded-xl shadow p-6 mb-6">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-2xl font-bold text-gray-800 mb-2">超参数调优</h1>
            <p class="text-gray-600">任务：{{ taskName }} - 算法：{{ algorithmName }}</p>
          </div>
          <div class="flex space-x-3">
            <button @click="startTuning" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
              开始调优
            </button>
            <button @click="stopTuning" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
              停止调优
            </button>
          </div>
        </div>
      </div>

      <!-- 主要内容区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 左侧：调优配置 -->
        <div class="space-y-6">
          <!-- 搜索空间配置 -->
          <div class="bg-white rounded-xl shadow p-6">
            <h2 class="text-lg font-semibold mb-4">搜索空间配置</h2>
            
            <div class="space-y-4">
              <div v-for="(param, index) in searchSpace" :key="index" class="border rounded p-4">
                <div class="flex justify-between items-center mb-2">
                  <h3 class="font-medium">{{ param.name }}</h3>
                  <button @click="removeParam(index)" class="text-red-500 hover:text-red-700">
                    <span>×</span>
                  </button>
                </div>
                
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label class="block text-sm text-gray-500 mb-1">参数类型</label>
                    <select v-model="param.type" class="w-full px-3 py-2 border border-gray-300 rounded-md">
                      <option value="continuous">连续</option>
                      <option value="discrete">离散</option>
                      <option value="categorical">分类</option>
                    </select>
                  </div>
                  
                  <div v-if="param.type === 'continuous'">
                    <label class="block text-sm text-gray-500 mb-1">范围</label>
                    <div class="flex space-x-2">
                      <input v-model.number="param.min" type="number" placeholder="最小值" 
                             class="flex-1 px-3 py-2 border border-gray-300 rounded-md">
                      <input v-model.number="param.max" type="number" placeholder="最大值" 
                             class="flex-1 px-3 py-2 border border-gray-300 rounded-md">
                    </div>
                  </div>
                  
                  <div v-if="param.type === 'discrete'">
                    <label class="block text-sm text-gray-500 mb-1">选项</label>
                    <input v-model="param.options" type="text" placeholder="用逗号分隔，如：1,2,4,8" 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md">
                  </div>
                  
                  <div v-if="param.type === 'categorical'">
                    <label class="block text-sm text-gray-500 mb-1">类别</label>
                    <input v-model="param.categories" type="text" placeholder="用逗号分隔，如：adam,sgd,rmsprop" 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md">
                  </div>
                </div>
              </div>
              
              <button @click="addParam" class="w-full border-2 border-dashed border-gray-300 rounded p-4 text-gray-500 hover:border-blue-500 hover:text-blue-500">
                + 添加参数
              </button>
            </div>
          </div>

          <!-- 调优策略配置 -->
          <div class="bg-white rounded-xl shadow p-6">
            <h2 class="text-lg font-semibold mb-4">调优策略配置</h2>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">优化算法</label>
                <select v-model="tuningConfig.optimizer" class="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="random">随机搜索</option>
                  <option value="bayesian">贝叶斯优化</option>
                  <option value="grid">网格搜索</option>
                  <option value="genetic">遗传算法</option>
                  <option value="tpe">TPE</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">最大试验次数</label>
                <input v-model.number="tuningConfig.maxTrials" type="number" min="1" max="1000" 
                       class="w-full px-3 py-2 border border-gray-300 rounded-md">
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">并行度</label>
                <input v-model.number="tuningConfig.parallelism" type="number" min="1" max="10" 
                       class="w-full px-3 py-2 border border-gray-300 rounded-md">
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">早停耐心</label>
                <input v-model.number="tuningConfig.patience" type="number" min="1" max="50" 
                       class="w-full px-3 py-2 border border-gray-300 rounded-md">
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">目标指标</label>
                <select v-model="tuningConfig.metric" class="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="attack_success_rate">攻击成功率</option>
                  <option value="perturbation_size">扰动大小</option>
                  <option value="computation_time">计算时间</option>
                  <option value="composite_score">综合评分</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">优化方向</label>
                <div class="flex space-x-4">
                  <label class="flex items-center">
                    <input v-model="tuningConfig.direction" type="radio" value="maximize" class="mr-2">
                    <span>最大化</span>
                  </label>
                  <label class="flex items-center">
                    <input v-model="tuningConfig.direction" type="radio" value="minimize" class="mr-2">
                    <span>最小化</span>
                  </label>
                </div>
              </div>
            </div>
            
            <div class="flex justify-end mt-4">
              <button @click="saveConfig" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                保存配置
              </button>
            </div>
          </div>
        </div>

        <!-- 右侧：调优结果和监控 -->
        <div class="space-y-6">
          <!-- 调优进度 -->
          <div class="bg-white rounded-xl shadow p-6">
            <h2 class="text-lg font-semibold mb-4">调优进度</h2>
            
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div class="bg-gray-50 p-4 rounded">
                <div class="text-sm text-gray-500">已完成试验</div>
                <div class="text-2xl font-bold text-blue-600">{{ progress.completedTrials }}</div>
              </div>
              <div class="bg-gray-50 p-4 rounded">
                <div class="text-sm text-gray-500">最佳得分</div>
                <div class="text-2xl font-bold text-green-600">{{ progress.bestScore }}</div>
              </div>
              <div class="bg-gray-50 p-4 rounded">
                <div class="text-sm text-gray-500">进度</div>
                <div class="text-2xl font-bold text-purple-600">{{ progress.percentage }}%</div>
              </div>
              <div class="bg-gray-50 p-4 rounded">
                <div class="text-sm text-gray-500">运行时间</div>
                <div class="text-2xl font-bold text-orange-600">{{ progress.runtime }}</div>
              </div>
            </div>
            
            <div class="mb-4">
              <div class="flex justify-between text-sm text-gray-500 mb-1">
                <span>调优进度</span>
                <span>{{ progress.percentage }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-blue-600 h-2 rounded-full" :style="{ width: progress.percentage + '%' }"></div>
              </div>
            </div>
          </div>

          <!-- 试验结果表格 -->
          <div class="bg-white rounded-xl shadow p-6">
            <h2 class="text-lg font-semibold mb-4">试验结果</h2>
            
            <div class="overflow-x-auto">
              <table class="w-full border-collapse">
                <thead>
                  <tr class="bg-gray-50">
                    <th class="border px-4 py-2 text-left">试验ID</th>
                    <th class="border px-4 py-2 text-left">得分</th>
                    <th class="border px-4 py-2 text-left">状态</th>
                    <th class="border px-4 py-2 text-left">参数</th>
                    <th class="border px-4 py-2 text-left">耗时</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="trial in trials" :key="trial.trialId" class="hover:bg-gray-50">
                    <td class="border px-4 py-2">{{ trial.trialId }}</td>
                    <td class="border px-4 py-2">{{ trial.score }}</td>
                    <td class="border px-4 py-2">
                      <span :class="getTrialStatusClass(trial.status)">{{ trial.status }}</span>
                    </td>
                    <td class="border px-4 py-2">{{ formatParams(trial.params) }}</td>
                    <td class="border px-4 py-2">{{ trial.duration }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 最佳参数展示 -->
          <div class="bg-white rounded-xl shadow p-6">
            <h2 class="text-lg font-semibold mb-4">最佳参数</h2>
            
            <div v-if="bestParams" class="space-y-3">
              <div v-for="(value, key) in bestParams" :key="key" class="flex justify-between items-center p-2 bg-gray-50 rounded">
                <span class="font-medium">{{ key }}</span>
                <span class="text-blue-600">{{ value }}</span>
              </div>
            </div>
            <div v-else class="text-gray-500 text-center py-8">
              暂无最佳参数
            </div>
          </div>
        </div>
      </div>

      <!-- 可视化图表区域 -->
      <div class="mt-6 bg-white rounded-xl shadow p-6">
        <h2 class="text-lg font-semibold mb-4">调优过程可视化</h2>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h3 class="text-md font-medium mb-3">得分分布</h3>
            <div class="h-48 bg-gray-100 rounded flex items-center justify-center">
              <span class="text-gray-500">图表区域 - 得分分布</span>
            </div>
          </div>
          
          <div>
            <h3 class="text-md font-medium mb-3">参数重要性</h3>
            <div class="h-48 bg-gray-100 rounded flex items-center justify-center">
              <span class="text-gray-500">图表区域 - 参数重要性</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { 
  getHyperParamHistory,
  startHyperParamTuning,
  saveHyperParams
} from '@/api.js'

const route = useRoute()
const taskId = route.params.taskId

// 任务信息
const taskName = ref('对抗样本生成任务')
const algorithmName = ref('FGSM')

// 搜索空间
const searchSpace = ref([
  {
    name: 'learning_rate',
    type: 'continuous',
    min: 0.0001,
    max: 0.1
  },
  {
    name: 'epsilon',
    type: 'continuous',
    min: 0.01,
    max: 0.5
  }
])

// 调优配置
const tuningConfig = reactive({
  optimizer: 'bayesian',
  maxTrials: 100,
  parallelism: 4,
  patience: 10,
  metric: 'attack_success_rate',
  direction: 'maximize'
})

// 调优进度
const progress = reactive({
  completedTrials: 0,
  bestScore: '0.00',
  percentage: 0,
  runtime: '00:00:00'
})

// 试验结果
const trials = ref([])

// 最佳参数
const bestParams = ref(null)

// 获取试验状态样式
const getTrialStatusClass = (status) => {
  const statusMap = {
    'completed': 'text-green-600',
    'running': 'text-blue-600',
    'failed': 'text-red-600',
    'pending': 'text-yellow-600'
  }
  return statusMap[status] || 'text-gray-600'
}

// 格式化参数显示
const formatParams = (params) => {
  if (typeof params === 'object') {
    return Object.entries(params).map(([key, value]) => `${key}: ${value}`).join(', ')
  }
  return params
}

// 添加参数
const addParam = () => {
  searchSpace.value.push({
    name: `param_${searchSpace.value.length + 1}`,
    type: 'continuous',
    min: 0,
    max: 1
  })
}

// 移除参数
const removeParam = (index) => {
  searchSpace.value.splice(index, 1)
}

// 保存配置
const saveConfig = async () => {
  try {
    await saveHyperParams(taskId, {
      searchSpace: searchSpace.value,
      config: tuningConfig
    })
    console.log('配置保存成功')
  } catch (error) {
    console.error('配置保存失败:', error)
  }
}

// 开始调优
const startTuning = async () => {
  try {
    await startHyperParamTuning(taskId, {
      searchSpace: searchSpace.value,
      config: tuningConfig
    })
    console.log('调优已开始')
    loadHistory()
  } catch (error) {
    console.error('调优启动失败:', error)
  }
}

// 停止调优
const stopTuning = () => {
  console.log('停止调优')
}

// 加载调优历史
const loadHistory = async () => {
  try {
    const response = await getHyperParamHistory(taskId)
    const data = response.data
    
    progress.completedTrials = data.completedTrials || 0
    progress.bestScore = data.bestScore || '0.00'
    progress.percentage = data.percentage || 0
    progress.runtime = data.runtime || '00:00:00'
    
    trials.value = data.trials || []
    bestParams.value = data.bestParams || null
  } catch (error) {
    console.error('加载调优历史失败:', error)
    // 使用模拟数据
    progress.completedTrials = 45
    progress.bestScore = '92.5'
    progress.percentage = 45
    progress.runtime = '01:23:45'
    
    trials.value = [
      {
        trialId: 1,
        score: '85.2',
        status: 'completed',
        params: { learning_rate: 0.01, epsilon: 0.1 },
        duration: '00:05:30'
      },
      {
        trialId: 2,
        score: '92.5',
        status: 'completed',
        params: { learning_rate: 0.008, epsilon: 0.12 },
        duration: '00:06:15'
      }
    ]
    
    bestParams.value = {
      learning_rate: 0.008,
      epsilon: 0.12,
      iterations: 100,
      optimizer: 'adam'
    }
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.el-form-item {
  margin-bottom: 16px;
}
</style> 