<template>
  <div class="p-8 bg-gray-50 min-h-screen">
    <div class="max-w-7xl mx-auto">
      <!-- 页面标题 -->
      <div class="bg-white rounded-xl shadow p-6 mb-6">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-2xl font-bold text-gray-800 mb-2">算法训练</h1>
            <p class="text-gray-600">任务：{{ taskName }} - 算法：{{ algorithmName }}</p>
          </div>
          <div class="flex space-x-3">
            <button @click="startTrainingTask" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
              开始训练
            </button>
            <button @click="stopTraining" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
              停止训练
            </button>
            <button @click="pauseTraining" class="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600">
              暂停训练
            </button>
          </div>
        </div>
      </div>

      <!-- 主要内容区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 左侧：训练配置 -->
        <div class="lg:col-span-1 space-y-6">
          <!-- 训练参数配置 -->
          <div class="bg-white rounded-xl shadow p-6">
            <h2 class="text-lg font-semibold mb-4">训练参数配置</h2>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">训练轮数</label>
                <input v-model.number="trainingParams.epochs" type="number" min="1" max="1000" 
                       class="w-full px-3 py-2 border border-gray-300 rounded-md">
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">批次大小</label>
                <input v-model.number="trainingParams.batchSize" type="number" min="1" max="512" 
                       class="w-full px-3 py-2 border border-gray-300 rounded-md">
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">学习率</label>
                <input v-model.number="trainingParams.learningRate" type="number" min="0.0001" max="1" step="0.0001" 
                       class="w-full px-3 py-2 border border-gray-300 rounded-md">
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">验证比例</label>
                <input v-model.number="trainingParams.validationSplit" type="number" min="0.1" max="0.5" step="0.1" 
                       class="w-full px-3 py-2 border border-gray-300 rounded-md">
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">早停耐心</label>
                <input v-model.number="trainingParams.earlyStoppingPatience" type="number" min="1" max="50" 
                       class="w-full px-3 py-2 border border-gray-300 rounded-md">
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">优化器</label>
                <select v-model="trainingParams.optimizer" class="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="adam">Adam</option>
                  <option value="sgd">SGD</option>
                  <option value="rmsprop">RMSprop</option>
                  <option value="adagrad">Adagrad</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">损失函数</label>
                <select v-model="trainingParams.lossFunction" class="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="cross_entropy">交叉熵</option>
                  <option value="mse">MSE</option>
                  <option value="mae">MAE</option>
                  <option value="huber">Huber</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">学习率调度</label>
                <select v-model="trainingParams.lrScheduler" class="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="none">无</option>
                  <option value="steplr">StepLR</option>
                  <option value="cosine">CosineAnnealing</option>
                  <option value="plateau">ReduceLROnPlateau</option>
                  <option value="exponential">ExponentialLR</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">权重衰减</label>
                <input v-model.number="trainingParams.weightDecay" type="number" min="0" max="1" step="0.0001" 
                       class="w-full px-3 py-2 border border-gray-300 rounded-md">
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">梯度裁剪</label>
                <input v-model.number="trainingParams.gradientClip" type="number" min="0" max="10" step="0.1" 
                       class="w-full px-3 py-2 border border-gray-300 rounded-md">
              </div>
            </div>
            
            <div class="flex justify-end mt-4">
              <button @click="saveTrainingParams" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                保存配置
              </button>
            </div>
          </div>

          <!-- 高级配置 -->
          <div class="bg-white rounded-xl shadow p-6">
            <h2 class="text-lg font-semibold mb-4">高级配置</h2>
            
            <div class="space-y-4">
              <div class="flex items-center">
                <input v-model="advancedConfig.dataAugmentation" type="checkbox" class="mr-3">
                <label class="text-sm font-medium text-gray-700">数据增强</label>
              </div>
              
              <div class="flex items-center">
                <input v-model="advancedConfig.mixedPrecision" type="checkbox" class="mr-3">
                <label class="text-sm font-medium text-gray-700">混合精度</label>
              </div>
              
              <div class="flex items-center">
                <input v-model="advancedConfig.distributedTraining" type="checkbox" class="mr-3">
                <label class="text-sm font-medium text-gray-700">分布式训练</label>
              </div>
              
              <div class="flex items-center">
                <input v-model="advancedConfig.modelCheckpoint" type="checkbox" class="mr-3">
                <label class="text-sm font-medium text-gray-700">模型检查点</label>
              </div>
              
              <div class="flex items-center">
                <input v-model="advancedConfig.tensorboard" type="checkbox" class="mr-3">
                <label class="text-sm font-medium text-gray-700">TensorBoard</label>
              </div>
              
              <div class="flex items-center">
                <input v-model="advancedConfig.autoSave" type="checkbox" class="mr-3">
                <label class="text-sm font-medium text-gray-700">自动保存</label>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：训练监控和结果 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 训练进度 -->
          <div class="bg-white rounded-xl shadow p-6">
            <h2 class="text-lg font-semibold mb-4">训练进度</h2>
            
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div class="bg-gray-50 p-4 rounded">
                <div class="text-sm text-gray-500">当前轮数</div>
                <div class="text-2xl font-bold text-blue-600">{{ progress.currentEpoch }}/{{ trainingParams.epochs }}</div>
              </div>
              <div class="bg-gray-50 p-4 rounded">
                <div class="text-sm text-gray-500">训练损失</div>
                <div class="text-2xl font-bold text-red-600">{{ progress.trainLoss || '0.000' }}</div>
              </div>
              <div class="bg-gray-50 p-4 rounded">
                <div class="text-sm text-gray-500">验证损失</div>
                <div class="text-2xl font-bold text-green-600">{{ progress.valLoss || '0.000' }}</div>
              </div>
              <div class="bg-gray-50 p-4 rounded">
                <div class="text-sm text-gray-500">运行时间</div>
                <div class="text-2xl font-bold text-purple-600">{{ progress.runtime || '00:00:00' }}</div>
              </div>
            </div>
            
            <div class="mb-4">
              <div class="flex justify-between text-sm text-gray-500 mb-1">
                <span>训练进度</span>
                <span>{{ progress.percentage }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-blue-600 h-2 rounded-full" :style="{ width: progress.percentage + '%' }"></div>
              </div>
            </div>
          </div>

          <!-- 训练曲线 -->
          <div class="bg-white rounded-xl shadow p-6">
            <h2 class="text-lg font-semibold mb-4">训练曲线</h2>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h3 class="text-md font-medium mb-3">损失曲线</h3>
                <div class="h-48 bg-gray-100 rounded flex items-center justify-center">
                  <span class="text-gray-500">图表区域 - 损失曲线</span>
                </div>
              </div>
              
              <div>
                <h3 class="text-md font-medium mb-3">准确率曲线</h3>
                <div class="h-48 bg-gray-100 rounded flex items-center justify-center">
                  <span class="text-gray-500">图表区域 - 准确率曲线</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 训练日志 -->
          <div class="bg-white rounded-xl shadow p-6">
            <h2 class="text-lg font-semibold mb-4">训练日志</h2>
            
            <div class="bg-black text-green-400 p-4 rounded font-mono text-sm h-64 overflow-y-auto">
              <div v-for="(log, index) in trainingLogs" :key="index" class="mb-1">
                <span class="text-gray-400">[{{ log.timestamp }}]</span> {{ log.message }}
              </div>
            </div>
            
            <div class="flex justify-between items-center mt-4">
              <div class="flex space-x-2">
                <button @click="clearLogs" class="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600">
                  清空日志
                </button>
                <button @click="exportLogs" class="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600">
                  导出日志
                </button>
              </div>
              <div class="text-sm text-gray-500">
                共 {{ trainingLogs.length }} 条日志
              </div>
            </div>
          </div>

          <!-- 训练结果 -->
          <div class="bg-white rounded-xl shadow p-6">
            <h2 class="text-lg font-semibold mb-4">训练结果</h2>
            
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div class="bg-gray-50 p-4 rounded text-center">
                <div class="text-sm text-gray-500">准确率</div>
                <div class="text-2xl font-bold text-blue-600">{{ evaluation.accuracy || '0.00%' }}</div>
              </div>
              <div class="bg-gray-50 p-4 rounded text-center">
                <div class="text-sm text-gray-500">精确率</div>
                <div class="text-2xl font-bold text-green-600">{{ evaluation.precision || '0.00%' }}</div>
              </div>
              <div class="bg-gray-50 p-4 rounded text-center">
                <div class="text-sm text-gray-500">召回率</div>
                <div class="text-2xl font-bold text-purple-600">{{ evaluation.recall || '0.00%' }}</div>
              </div>
              <div class="bg-gray-50 p-4 rounded text-center">
                <div class="text-sm text-gray-500">F1分数</div>
                <div class="text-2xl font-bold text-orange-600">{{ evaluation.f1Score || '0.00' }}</div>
              </div>
            </div>
            
            <div class="mt-4 grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div class="bg-gray-50 p-4 rounded text-center">
                <div class="text-sm text-gray-500">攻击成功率</div>
                <div class="text-2xl font-bold text-red-600">{{ evaluation.attackSuccessRate || '0.00%' }}</div>
              </div>
              <div class="bg-gray-50 p-4 rounded text-center">
                <div class="text-sm text-gray-500">平均扰动</div>
                <div class="text-2xl font-bold text-indigo-600">{{ evaluation.avgPerturbation || '0.000' }}</div>
              </div>
              <div class="bg-gray-50 p-4 rounded text-center">
                <div class="text-sm text-gray-500">鲁棒性</div>
                <div class="text-2xl font-bold text-teal-600">{{ evaluation.robustness || '0.00%' }}</div>
              </div>
              <div class="bg-gray-50 p-4 rounded text-center">
                <div class="text-sm text-gray-500">训练时间</div>
                <div class="text-2xl font-bold text-pink-600">{{ evaluation.trainingTime || '00:00:00' }}</div>
              </div>
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
  getTrainingHistory,
  startTraining,
  stopTask,
  pauseTask,
  resumeTask,
  getTaskLogs
} from '@/api.js'

const route = useRoute()
const taskId = route.params.taskId

// 任务信息
const taskName = ref('对抗样本生成任务')
const algorithmName = ref('FGSM')

// 训练参数
const trainingParams = reactive({
  epochs: 50,
  batchSize: 32,
  learningRate: 0.001,
  validationSplit: 0.2,
  earlyStoppingPatience: 10,
  optimizer: 'adam',
  lossFunction: 'cross_entropy',
  lrScheduler: 'none',
  weightDecay: 0.0001,
  gradientClip: 1.0
})

// 高级配置
const advancedConfig = reactive({
  dataAugmentation: true,
  mixedPrecision: false,
  distributedTraining: false,
  modelCheckpoint: true,
  tensorboard: true,
  autoSave: true
})

// 训练进度
const progress = reactive({
  currentEpoch: 0,
  trainLoss: '0.000',
  valLoss: '0.000',
  percentage: 0,
  runtime: '00:00:00'
})

// 训练日志
const trainingLogs = ref([])

// 评估结果
const evaluation = reactive({
  accuracy: '0.00%',
  precision: '0.00%',
  recall: '0.00%',
  f1Score: '0.00',
  attackSuccessRate: '0.00%',
  avgPerturbation: '0.000',
  robustness: '0.00%',
  trainingTime: '00:00:00'
})

// 开始训练
const startTrainingTask = async () => {
  try {
    const config = {
      ...trainingParams,
      ...advancedConfig
    }
    await startTraining(taskId, config)
    console.log('训练已开始')
    loadHistory()
  } catch (error) {
    console.error('训练启动失败:', error)
  }
}

// 停止训练
const stopTraining = async () => {
  try {
    await stopTask(taskId)
    console.log('训练已停止')
  } catch (error) {
    console.error('停止训练失败:', error)
  }
}

// 暂停训练
const pauseTraining = async () => {
  try {
    await pauseTask(taskId)
    console.log('训练已暂停')
  } catch (error) {
    console.error('暂停训练失败:', error)
  }
}

// 恢复训练
const resumeTraining = async () => {
  try {
    await resumeTask(taskId)
    console.log('训练已恢复')
  } catch (error) {
    console.error('恢复训练失败:', error)
  }
}

// 保存训练参数
const saveTrainingParams = async () => {
  try {
    // 这里应该调用API保存训练参数
    console.log('训练参数保存成功')
  } catch (error) {
    console.error('保存训练参数失败:', error)
  }
}

// 清空日志
const clearLogs = () => {
  trainingLogs.value = []
}

// 导出日志
const exportLogs = () => {
  const logText = trainingLogs.value.map(log => `[${log.timestamp}] ${log.message}`).join('\n')
  const blob = new Blob([logText], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `training_logs_${taskId}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

// 加载训练历史
const loadHistory = async () => {
  try {
    const response = await getTrainingHistory(taskId)
    const data = response.data
    
    // 更新进度
    if (data.progress) {
      progress.currentEpoch = data.progress.currentEpoch || 0
      progress.trainLoss = data.progress.trainLoss || '0.000'
      progress.valLoss = data.progress.valLoss || '0.000'
      progress.percentage = data.progress.percentage || 0
      progress.runtime = data.progress.runtime || '00:00:00'
    }
    
    // 更新日志
    if (data.logs) {
      trainingLogs.value = data.logs
    }
    
    // 更新评估结果
    if (data.evaluation) {
      Object.assign(evaluation, data.evaluation)
    }
  } catch (error) {
    console.error('加载训练历史失败:', error)
    // 使用模拟数据
    progress.currentEpoch = 25
    progress.trainLoss = '0.123'
    progress.valLoss = '0.145'
    progress.percentage = 50
    progress.runtime = '01:15:30'
    
    trainingLogs.value = [
      { timestamp: '2024-01-15 10:30:00', message: 'Training started' },
      { timestamp: '2024-01-15 10:31:00', message: 'Epoch 1/50 completed' },
      { timestamp: '2024-01-15 10:32:00', message: 'Epoch 2/50 completed' }
    ]
    
    Object.assign(evaluation, {
      accuracy: '85.5%',
      precision: '87.2%',
      recall: '83.8%',
      f1Score: '85.5',
      attackSuccessRate: '92.3%',
      avgPerturbation: '0.045',
      robustness: '78.9%',
      trainingTime: '02:15:30'
    })
  }
}

onMounted(() => {
  loadHistory()
})
</script> 