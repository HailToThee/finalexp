<template>
  <div class="p-8 bg-gray-50 min-h-screen">
    <div class="max-w-7xl mx-auto">
      <!-- 页面标题 -->
      <div class="bg-white rounded-xl shadow p-6 mb-6">
        <h1 class="text-2xl font-bold text-gray-800 mb-2">对抗样本生成</h1>
        <p class="text-gray-600">AI模型安全性评估 - 对抗样本生成与超参数调优</p>
      </div>

      <!-- 主要功能区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 左侧：任务管理 -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-xl shadow p-6">
            <h2 class="text-lg font-semibold mb-4">任务管理</h2>
            
            <!-- 新建任务按钮 -->
            <button @click="showCreateTask = true" class="w-full bg-blue-500 text-white px-4 py-3 rounded-lg hover:bg-blue-600 mb-4">
              <span class="mr-2">+</span>新建对抗样本任务
            </button>

            <!-- 任务列表 -->
            <div class="space-y-3">
              <div v-for="task in tasks" :key="task.id" 
                   class="p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
                   :class="{ 'border-blue-500 bg-blue-50': selectedTask?.id === task.id }"
                   @click="selectTask(task)">
                <div class="flex justify-between items-start">
                  <div>
                    <h3 class="font-medium text-gray-800">{{ task.name }}</h3>
                    <p class="text-sm text-gray-500">{{ task.description }}</p>
                  </div>
                  <span :class="getStatusClass(task.status)" class="text-xs px-2 py-1 rounded">
                    {{ task.status }}
                  </span>
                </div>
                <div class="text-xs text-gray-400 mt-2">
                  {{ task.createdAt }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：任务详情和配置 -->
        <div class="lg:col-span-2">
          <div v-if="selectedTask" class="space-y-6">
            <!-- 任务基本信息 -->
            <div class="bg-white rounded-xl shadow p-6">
              <div class="flex justify-between items-center mb-4">
                <h2 class="text-lg font-semibold">{{ selectedTask.name }}</h2>
                <div class="flex space-x-2">
                  <button @click="editTask" class="bg-yellow-500 text-white px-3 py-1 rounded text-sm hover:bg-yellow-600">
                    编辑
                  </button>
                  <button @click="deleteTask" class="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600">
                    删除
                  </button>
                </div>
              </div>
              
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span class="text-gray-500">状态：</span>
                  <span :class="getStatusClass(selectedTask.status)">{{ selectedTask.status }}</span>
                </div>
                <div>
                  <span class="text-gray-500">创建时间：</span>
                  <span>{{ selectedTask.createdAt }}</span>
                </div>
                <div>
                  <span class="text-gray-500">算法：</span>
                  <span>{{ selectedTask.algorithm }}</span>
                </div>
                <div>
                  <span class="text-gray-500">目标模型：</span>
                  <span>{{ selectedTask.targetModel }}</span>
                </div>
              </div>
            </div>

            <!-- 超参数配置 -->
            <div class="bg-white rounded-xl shadow p-6">
              <h3 class="text-lg font-semibold mb-4">超参数配置</h3>
              
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">学习率</label>
                  <input v-model.number="hyperParams.learningRate" type="number" min="0.0001" max="1" step="0.0001" 
                         class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">迭代次数</label>
                  <input v-model.number="hyperParams.iterations" type="number" min="1" max="1000" 
                         class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">扰动大小</label>
                  <input v-model.number="hyperParams.epsilon" type="number" min="0.001" max="1" step="0.001" 
                         class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">批次大小</label>
                  <input v-model.number="hyperParams.batchSize" type="number" min="1" max="128" 
                         class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">优化器</label>
                  <select v-model="hyperParams.optimizer" 
                          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="adam">Adam</option>
                    <option value="sgd">SGD</option>
                    <option value="rmsprop">RMSprop</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">损失函数</label>
                  <select v-model="hyperParams.lossFunction" 
                          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="cross_entropy">交叉熵</option>
                    <option value="kl_divergence">KL散度</option>
                    <option value="mse">MSE</option>
                  </select>
                </div>
              </div>

              <div class="flex justify-end space-x-3 mt-4">
                <button @click="saveHyperParamsConfig" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                  保存配置
                </button>
                <button @click="startHyperParamTuningTask" class="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600">
                  开始超参数调优
                </button>
              </div>
            </div>

            <!-- 训练配置 -->
            <div class="bg-white rounded-xl shadow p-6">
              <h3 class="text-lg font-semibold mb-4">算法训练配置</h3>
              
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">训练轮数</label>
                  <input v-model.number="trainingConfig.epochs" type="number" min="1" max="1000" 
                         class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">验证比例</label>
                  <input v-model.number="trainingConfig.validationSplit" type="number" min="0.1" max="0.5" step="0.1" 
                         class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">早停耐心</label>
                  <input v-model.number="trainingConfig.earlyStoppingPatience" type="number" min="1" max="50" 
                         class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">学习率调度</label>
                  <select v-model="trainingConfig.lrScheduler" 
                          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="none">无</option>
                    <option value="steplr">StepLR</option>
                    <option value="cosine">CosineAnnealing</option>
                    <option value="plateau">ReduceLROnPlateau</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">数据增强</label>
                  <input v-model="trainingConfig.dataAugmentation" type="checkbox" class="mr-2">
                  <span class="text-sm text-gray-600">启用数据增强</span>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">混合精度</label>
                  <input v-model="trainingConfig.mixedPrecision" type="checkbox" class="mr-2">
                  <span class="text-sm text-gray-600">启用混合精度</span>
                </div>
              </div>

              <div class="flex justify-end space-x-3 mt-4">
                <button @click="saveTrainingConfigTask" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                  保存配置
                </button>
                <button @click="startTrainingTask" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                  开始训练
                </button>
              </div>
            </div>

            <!-- 实时监控 -->
            <div class="bg-white rounded-xl shadow p-6">
              <h3 class="text-lg font-semibold mb-4">实时监控</h3>
              
              <div class="grid grid-cols-2 gap-4 mb-4">
                <div class="bg-gray-50 p-4 rounded">
                  <div class="text-sm text-gray-500">当前损失</div>
                  <div class="text-2xl font-bold text-blue-600">{{ monitoring.currentLoss || '0.000' }}</div>
                </div>
                <div class="bg-gray-50 p-4 rounded">
                  <div class="text-sm text-gray-500">攻击成功率</div>
                  <div class="text-2xl font-bold text-green-600">{{ monitoring.attackSuccessRate || '0.00%' }}</div>
                </div>
                <div class="bg-gray-50 p-4 rounded">
                  <div class="text-sm text-gray-500">训练进度</div>
                  <div class="text-2xl font-bold text-purple-600">{{ monitoring.progress || '0%' }}</div>
                </div>
                <div class="bg-gray-50 p-4 rounded">
                  <div class="text-sm text-gray-500">运行时间</div>
                  <div class="text-2xl font-bold text-orange-600">{{ monitoring.runtime || '00:00:00' }}</div>
                </div>
              </div>

              <!-- 进度条 -->
              <div class="mb-4">
                <div class="flex justify-between text-sm text-gray-500 mb-1">
                  <span>训练进度</span>
                  <span>{{ monitoring.progress || '0%' }}</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div class="bg-blue-600 h-2 rounded-full" :style="{ width: monitoring.progress || '0%' }"></div>
                </div>
              </div>

              <!-- 日志输出 -->
              <div class="bg-black text-green-400 p-4 rounded font-mono text-sm h-32 overflow-y-auto">
                <div v-for="(log, index) in monitoring.logs" :key="index" class="mb-1">
                  {{ log }}
                </div>
              </div>
            </div>
          </div>

          <!-- 未选择任务时的提示 -->
          <div v-else class="bg-white rounded-xl shadow p-12 text-center">
            <div class="text-6xl text-gray-300 mb-4">📁</div>
            <h3 class="text-lg font-medium text-gray-600 mb-2">请选择一个任务</h3>
            <p class="text-gray-500">从左侧任务列表中选择一个任务来查看详情和配置</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建任务弹窗 -->
    <div v-if="showCreateTask" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-4">新建对抗样本任务</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">任务名称 *</label>
            <input v-model="newTask.name" type="text" placeholder="请输入任务名称" 
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">任务描述</label>
            <textarea v-model="newTask.description" placeholder="请输入任务描述" rows="3"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">选择算法 *</label>
            <select v-model="newTask.algorithmId" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">请选择对抗算法</option>
              <option v-for="algo in availableAlgorithms" :key="algo.id" :value="algo.id">{{ algo.name }}</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">目标模型 *</label>
            <select v-model="newTask.targetModelId" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">请选择目标模型</option>
              <option v-for="model in availableModels" :key="model.id" :value="model.id">{{ model.name }}</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">数据集 *</label>
            <select v-model="newTask.datasetId" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">请选择数据集</option>
              <option v-for="dataset in availableDatasets" :key="dataset.id" :value="dataset.id">{{ dataset.name }}</option>
            </select>
          </div>
        </div>
        
        <div class="flex justify-end space-x-3 mt-6">
          <button @click="showCreateTask = false" class="px-4 py-2 text-gray-600 hover:text-gray-800">
            取消
          </button>
          <button @click="createTask" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            创建任务
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { 
  fetchAdversarialTasks, 
  createAdversarialTask, 
  updateAdversarialTask, 
  deleteAdversarialTask,
  fetchAvailableAlgorithms,
  fetchAvailableModels,
  fetchAvailableDatasets,
  saveHyperParams,
  startHyperParamTuning,
  saveTrainingConfig,
  startTraining,
  getTaskMonitoring
} from '@/api.js'

// 响应式数据
const tasks = ref([])
const selectedTask = ref(null)
const showCreateTask = ref(false)
const availableAlgorithms = ref([])
const availableModels = ref([])
const availableDatasets = ref([])

// 新建任务表单
const newTask = reactive({
  name: '',
  description: '',
  algorithmId: '',
  targetModelId: '',
  datasetId: ''
})

// 超参数配置
const hyperParams = reactive({
  learningRate: 0.01,
  iterations: 100,
  epsilon: 0.1,
  batchSize: 32,
  optimizer: 'adam',
  lossFunction: 'cross_entropy'
})

// 训练配置
const trainingConfig = reactive({
  epochs: 50,
  validationSplit: 0.2,
  earlyStoppingPatience: 10,
  lrScheduler: 'none',
  dataAugmentation: true,
  mixedPrecision: false
})

// 监控数据
const monitoring = reactive({
  currentLoss: '0.000',
  attackSuccessRate: '0.00%',
  progress: '0%',
  runtime: '00:00:00',
  logs: []
})

// 获取状态样式类
const getStatusClass = (status) => {
  const statusMap = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'running': 'bg-blue-100 text-blue-800',
    'completed': 'bg-green-100 text-green-800',
    'failed': 'bg-red-100 text-red-800',
    'paused': 'bg-gray-100 text-gray-800'
  }
  return statusMap[status] || 'bg-gray-100 text-gray-800'
}

// 选择任务
const selectTask = (task) => {
  selectedTask.value = task
  loadTaskConfig(task.id)
  startMonitoring(task.id)
}

// 加载任务配置
const loadTaskConfig = async (taskId) => {
  try {
    // 这里应该调用API获取任务的超参数和训练配置
    // const config = await getTaskConfig(taskId)
    // Object.assign(hyperParams, config.hyperParams)
    // Object.assign(trainingConfig, config.trainingConfig)
  } catch (error) {
    console.error('加载任务配置失败:', error)
  }
}

// 开始监控
const startMonitoring = (taskId) => {
  // 模拟实时监控数据更新
  const interval = setInterval(async () => {
    if (selectedTask.value?.id === taskId) {
      try {
        const data = await getTaskMonitoring(taskId)
        Object.assign(monitoring, data)
      } catch (error) {
        console.error('获取监控数据失败:', error)
      }
    } else {
      clearInterval(interval)
    }
  }, 2000)
}

// 创建任务
const createTask = async () => {
  try {
    const response = await createAdversarialTask(newTask)
    console.log('任务创建成功:', response)
    showCreateTask.value = false
    resetTaskForm()
    loadTasks()
  } catch (error) {
    console.error('任务创建失败:', error)
  }
}

// 编辑任务
const editTask = () => {
  // 实现编辑任务逻辑
  console.log('编辑功能开发中')
}

// 删除任务
const deleteTask = async () => {
  try {
    if (confirm('确定要删除这个任务吗？')) {
      await deleteAdversarialTask(selectedTask.value.id)
      console.log('任务删除成功')
      selectedTask.value = null
      loadTasks()
    }
  } catch (error) {
    console.error('任务删除失败:', error)
  }
}

// 保存超参数配置
const saveHyperParamsConfig = async () => {
  try {
    await saveHyperParams(selectedTask.value.id, hyperParams)
    console.log('超参数配置保存成功')
  } catch (error) {
    console.error('超参数配置保存失败:', error)
  }
}

// 开始超参数调优
const startHyperParamTuningTask = async () => {
  try {
    await startHyperParamTuning(selectedTask.value.id, hyperParams)
    console.log('超参数调优已开始')
  } catch (error) {
    console.error('超参数调优启动失败:', error)
  }
}

// 保存训练配置
const saveTrainingConfigTask = async () => {
  try {
    await saveTrainingConfig(selectedTask.value.id, trainingConfig)
    console.log('训练配置保存成功')
  } catch (error) {
    console.error('训练配置保存失败:', error)
  }
}

// 开始训练
const startTrainingTask = async () => {
  try {
    await startTraining(selectedTask.value.id, trainingConfig)
    console.log('训练已开始')
  } catch (error) {
    console.error('训练启动失败:', error)
  }
}

// 重置任务表单
const resetTaskForm = () => {
  Object.assign(newTask, {
    name: '',
    description: '',
    algorithmId: '',
    targetModelId: '',
    datasetId: ''
  })
}

// 加载任务列表
const loadTasks = async () => {
  try {
    const response = await fetchAdversarialTasks()
    tasks.value = response.data.tasks || []
  } catch (error) {
    console.error('加载任务列表失败:', error)
    // 使用模拟数据
    tasks.value = [
      {
        id: 1,
        name: 'FGSM对抗样本生成',
        description: '使用FGSM算法生成对抗样本',
        status: 'running',
        createdAt: '2024-01-15 10:30',
        algorithm: 'FGSM',
        targetModel: 'ResNet50'
      },
      {
        id: 2,
        name: 'PGD攻击实验',
        description: '使用PGD算法进行攻击实验',
        status: 'completed',
        createdAt: '2024-01-14 15:20',
        algorithm: 'PGD',
        targetModel: 'VGG16'
      }
    ]
  }
}

// 加载可用算法
const loadAvailableAlgorithms = async () => {
  try {
    const response = await fetchAvailableAlgorithms()
    availableAlgorithms.value = response.data.algorithms || []
  } catch (error) {
    console.error('加载算法列表失败:', error)
    // 使用模拟数据
    availableAlgorithms.value = [
      { id: 1, name: 'FGSM' },
      { id: 2, name: 'PGD' },
      { id: 3, name: 'CW' },
      { id: 4, name: 'DeepFool' }
    ]
  }
}

// 加载可用模型
const loadAvailableModels = async () => {
  try {
    const response = await fetchAvailableModels()
    availableModels.value = response.data.models || []
  } catch (error) {
    console.error('加载模型列表失败:', error)
    // 使用模拟数据
    availableModels.value = [
      { id: 1, name: 'ResNet50' },
      { id: 2, name: 'VGG16' },
      { id: 3, name: 'InceptionV3' }
    ]
  }
}

// 加载可用数据集
const loadAvailableDatasets = async () => {
  try {
    const response = await fetchAvailableDatasets()
    availableDatasets.value = response.data.datasets || []
  } catch (error) {
    console.error('加载数据集列表失败:', error)
    // 使用模拟数据
    availableDatasets.value = [
      { id: 1, name: 'CIFAR-10' },
      { id: 2, name: 'ImageNet' },
      { id: 3, name: 'MNIST' }
    ]
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadTasks()
  loadAvailableAlgorithms()
  loadAvailableModels()
  loadAvailableDatasets()
})
</script>

<style scoped>
.el-form-item {
  margin-bottom: 16px;
}
</style> 