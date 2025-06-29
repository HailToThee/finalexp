<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">算法调试与运行日志</h2>
    <div class="mb-4 flex items-center">
      <select v-model="selectedAlgorithmId" class="border rounded px-2 py-1 mr-2">
        <option disabled value="">请选择算法</option>
        <option v-for="algo in algorithms" :key="algo.id" :value="algo.id">{{ algo.name }}</option>
      </select>
      <button @click="fetchAlgorithmInfo" class="bg-blue-500 text-white px-4 py-1 rounded mr-2">查看详情</button>
      <button @click="debugDialog=true" class="bg-green-500 text-white px-4 py-1 rounded">在线调试</button>
    </div>
    <div v-if="algorithmInfo" class="mb-6">
      <h3 class="font-bold mb-2">算法信息</h3>
      <div class="mb-2">名称：{{ algorithmInfo.name }}</div>
      <div class="mb-2">类型：{{ algorithmInfo.type }}</div>
      <div class="mb-2">描述：{{ algorithmInfo.description }}</div>
      <div class="mb-2">支持资源：{{ algorithmInfo.resources }}</div>
    </div>
    <div>
      <h3 class="font-bold mb-2">运行日志与统计</h3>
      <table class="min-w-full bg-white border">
        <thead>
          <tr>
            <th class="border px-4 py-2">运行时间</th>
            <th class="border px-4 py-2">参数</th>
            <th class="border px-4 py-2">ASR</th>
            <th class="border px-4 py-2">扰动大小</th>
            <th class="border px-4 py-2">可视化对比</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in debugLogs" :key="log.id">
            <td class="border px-4 py-2">{{ log.time }}</td>
            <td class="border px-4 py-2">{{ log.params }}</td>
            <td class="border px-4 py-2">{{ log.asr }}</td>
            <td class="border px-4 py-2">{{ log.perturbation }}</td>
            <td class="border px-4 py-2">
              <img v-if="log.visualization" :src="log.visualization" class="max-w-[80px] border rounded" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- 在线调试弹窗 -->
    <div v-if="debugDialog" class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded shadow-lg w-[30rem]">
        <h3 class="text-lg font-bold mb-2">在线调试</h3>
        <div class="mb-2">算法：{{ selectedAlgorithmName }}</div>
        <input v-model="debugParams" placeholder="参数（如攻击强度等）" class="border w-full mb-2 px-2 py-1" />
        <select v-model="debugResource" class="border w-full mb-2 px-2 py-1">
          <option disabled value="">请选择资源</option>
          <option value="CPU">CPU</option>
          <option value="GPU">GPU</option>
        </select>
        <button @click="runDebug" class="bg-green-500 text-white px-4 py-1 rounded mr-2">运行</button>
        <button @click="debugDialog=false" class="bg-gray-300 px-4 py-1 rounded">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAlgorithmInfo, getDebugLogs, runDebug } from '@/api.js'

const algorithms = ref([])
const selectedAlgorithmId = ref('')
const algorithmInfo = ref(null)
const debugDialog = ref(false)
const debugParams = ref('')
const debugResource = ref('')
const debugLogs = ref([])

const selectedAlgorithmName = computed(() => {
  const algo = algorithms.value.find(a => a.id === selectedAlgorithmId.value)
  return algo ? algo.name : ''
})

async function fetchAlgorithms() {
  try {
    const res = await axios.get('/api/algorithm/list')
    algorithms.value = res.data.algorithms || []
  } catch (err) {
    console.error('获取算法列表失败', err)
  }
}

async function fetchAlgorithmInfo() {
  if (!selectedAlgorithmId.value) return
  try {
    const res = await getAlgorithmInfo(selectedAlgorithmId.value)
    algorithmInfo.value = res.data
    debugLogs.value = await getDebugLogsData(selectedAlgorithmId.value)
  } catch (err) {
    console.error('获取算法详情失败', err)
  }
}

async function getDebugLogsData(id) {
  try {
    const res = await getDebugLogs(id)
    return res.data.logs || []
  } catch (err) {
    console.error('获取调试日志失败', err)
    return []
  }
}

async function runDebug() {
  try {
    await runDebug({
      algorithm_id: selectedAlgorithmId.value,
      params: debugParams.value,
      resource: debugResource.value,
    })
    debugDialog.value = false
    debugParams.value = ''
    debugResource.value = ''
    await fetchAlgorithmInfo()
  } catch (err) {
    console.error('运行调试失败', err)
    alert('调试任务启动失败')
  }
}

onMounted(() => {
  fetchAlgorithms()
})
</script>

<style scoped>
/* 可根据需要自定义样式 */
</style> 