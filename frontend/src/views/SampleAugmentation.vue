<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">样本扩增与分析</h2>
    <div class="mb-4 flex items-center">
      <select v-model="selectedSampleId" class="border rounded px-2 py-1 mr-2">
        <option disabled value="">请选择样本集</option>
        <option v-for="sample in samples" :key="sample.id" :value="sample.id">{{ sample.name }}</option>
      </select>
      <button @click="fetchSampleInfo" class="bg-blue-500 text-white px-4 py-1 rounded mr-2">分析</button>
      <button @click="augmentationDialog=true" class="bg-green-500 text-white px-4 py-1 rounded">扩增样本</button>
    </div>
    <div v-if="sampleInfo" class="mb-6">
      <h3 class="font-bold mb-2">样本分析</h3>
      <div class="mb-2">样本总数：{{ sampleInfo.count }}</div>
      <div class="mb-2">类别分布：<span v-for="(v,k) in sampleInfo.class_dist" :key="k">{{ k }}:{{ v }} </span></div>
      <div class="mb-2">图像分析：{{ sampleInfo.image_analysis }}</div>
      <div class="mb-2">标注分析：{{ sampleInfo.label_analysis }}</div>
      <img v-if="sampleInfo.visualization" :src="sampleInfo.visualization" class="max-w-xs border rounded" />
    </div>
    <div>
      <h3 class="font-bold mb-2">扩增历史</h3>
      <table class="min-w-full bg-white border">
        <thead>
          <tr>
            <th class="border px-4 py-2">扩增方式</th>
            <th class="border px-4 py-2">参数</th>
            <th class="border px-4 py-2">扩增后样本数</th>
            <th class="border px-4 py-2">时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in augmentationHistory" :key="item.id">
            <td class="border px-4 py-2">{{ item.method }}</td>
            <td class="border px-4 py-2">{{ item.params }}</td>
            <td class="border px-4 py-2">{{ item.count }}</td>
            <td class="border px-4 py-2">{{ item.time }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- 扩增弹窗 -->
    <div v-if="augmentationDialog" class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded shadow-lg w-96">
        <h3 class="text-lg font-bold mb-2">扩增样本</h3>
        <select v-model="augmentation.method" class="border w-full mb-2 px-2 py-1">
          <option disabled value="">请选择扩增方式</option>
          <option value="水平翻转">水平翻转</option>
          <option value="垂直翻转">垂直翻转</option>
          <option value="随机旋转">随机旋转</option>
          <option value="随机缩放">随机缩放</option>
          <option value="高斯模糊">高斯模糊</option>
          <option value="曝光">曝光</option>
          <option value="平移">平移</option>
        </select>
        <input v-model="augmentation.params" placeholder="参数（如角度、比例等）" class="border w-full mb-2 px-2 py-1" />
        <button @click="doAugmentation" class="bg-green-500 text-white px-4 py-1 rounded mr-2">确定</button>
        <button @click="augmentationDialog=false" class="bg-gray-300 px-4 py-1 rounded">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchSamples, uploadSample, deleteSample, getSampleInfo } from '@/api.js'

const allSamples = ref([])
const selectedSampleId = ref('')
const sampleInfo = ref(null)
const augmentationDialog = ref(false)
const augmentation = ref({ method: '', params: '' })
const augmentationHistory = ref([])

// 获取样本列表
async function fetchSamplesData() {
  try {
    const res = await fetchSamples()
    allSamples.value = res.data.samples || []
  } catch (e) {
    allSamples.value = []
  }
}

onMounted(() => {
  fetchSamplesData()
})

// 上传样本
async function handleFileChange(e) {
  const fileList = e.target.files
  if (fileList.length > 0) {
    const file = fileList[0]
    const formData = new FormData()
    formData.append('file', file)
    try {
      await uploadSample(formData)
      await fetchSamplesData()
      alert('上传成功')
    } catch (err) {
      alert('上传失败')
    }
  }
}

// 删除样本
async function deleteSampleConfirm() {
  if (!deleteTarget.value) return
  try {
    await deleteSample(deleteTarget.value.id)
    await fetchSamplesData()
    showDeleteConfirm.value = false
    deleteTarget.value = null
    alert('样本删除成功')
  } catch (err) {
    alert('样本删除失败')
  }
}

// 获取样本详情
async function getSampleDetail(id) {
  try {
    const res = await getSampleInfo(id)
    return res.data
  } catch (err) {
    return null
  }
}

async function fetchSampleInfo() {
  if (!selectedSampleId.value) return;
  const res = await getSampleDetail(selectedSampleId.value);
  sampleInfo.value = res;
  fetchAugmentationHistory();
}

async function fetchAugmentationHistory() {
  const res = await getSampleDetail(`${selectedSampleId.value}/augmentation/history`);
  augmentationHistory.value = res.history || [];
}

async function doAugmentation() {
  await getSampleDetail(`${selectedSampleId.value}/augmentation`, {
    method: augmentation.value.method,
    params: augmentation.value.params,
  });
  augmentationDialog.value = false;
  augmentation.value = { method: '', params: '' };
  fetchSampleInfo();
}
</script>

<style scoped>
/* 可根据需要自定义样式 */
</style> 