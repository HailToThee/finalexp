<template>
  <div class="flex min-h-screen bg-gray-50">
    <!-- 左侧树形导航 -->
    <div class="w-64 bg-white shadow-lg rounded-r-2xl p-6 mr-8 mt-8 h-fit">
      <div class="font-bold text-lg mb-4">样本分组</div>
      <ul>
        <li :class="['cursor-pointer px-3 py-2 rounded mb-1', selectedGroup===1 ? 'bg-blue-100 text-blue-600 font-bold' : 'hover:bg-gray-100']" @click="selectGroup(1)">全部样本</li>
        <li v-for="g in sampleGroups[0].children" :key="g.id" :class="['cursor-pointer px-3 py-2 rounded mb-1', selectedGroup===g.id ? 'bg-blue-100 text-blue-600 font-bold' : 'hover:bg-gray-100']" @click="selectGroup(g.id)">{{ g.name }}</li>
      </ul>
    </div>
    <!-- 主内容区 -->
    <div class="flex-1 max-w-6xl mx-auto p-8">
      <div class="bg-white rounded-xl shadow p-8">
        <!-- 顶部筛选和操作 -->
        <div class="flex items-center mb-6 justify-between">
          <div class="flex space-x-2">
            <input v-model="searchName" type="text" placeholder="样本名" class="border rounded px-3 py-2 focus:outline-none focus:ring w-48" />
            <input v-model="searchUploader" type="text" placeholder="上传人" class="border rounded px-3 py-2 focus:outline-none focus:ring w-32" />
            <select v-model="searchType" class="border rounded px-3 py-2 focus:outline-none focus:ring w-32">
              <option value="">全部类型</option>
              <option value="文本">文本</option>
              <option value="图片">图片</option>
              <option value="音频">音频</option>
            </select>
            <button @click="filterSamples" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">查询</button>
            <button @click="resetFilters" class="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300">重置</button>
          </div>
          <div class="flex space-x-2">
            <button @click="showAddForm=true" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">+ 新建样本集</button>
            <button @click="showDistChart=true" class="bg-blue-400 text-white px-4 py-2 rounded hover:bg-blue-500">样本分布</button>
            <button @click="viewMode='table'" :class="viewMode==='table' ? 'bg-gray-800 text-white' : 'bg-gray-200'" class="px-3 py-1 rounded">表格</button>
            <button @click="viewMode='grid'" :class="viewMode==='grid' ? 'bg-gray-800 text-white' : 'bg-gray-200'" class="px-3 py-1 rounded">网格</button>
          </div>
        </div>
        <!-- 样本表格视图 -->
        <div v-if="viewMode==='table'" class="bg-gray-50 rounded-lg shadow-inner p-4">
          <table class="min-w-full text-sm">
            <thead class="bg-gray-100">
              <tr>
                <th class="py-2 px-4 border-b"><input type="checkbox" @change="toggleAll" :checked="allSelected" /></th>
                <th class="py-2 px-4 border-b">样本名</th>
                <th class="py-2 px-4 border-b">类型</th>
                <th class="py-2 px-4 border-b">上传人</th>
                <th class="py-2 px-4 border-b">上传时间</th>
                <th class="py-2 px-4 border-b">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="sample in pagedSamples" :key="sample.id" class="hover:bg-blue-50">
                <td class="py-2 px-4 border-b"><input type="checkbox" v-model="selectedSamples" :value="sample.id" /></td>
                <td class="py-2 px-4 border-b">{{ sample.name }}</td>
                <td class="py-2 px-4 border-b">{{ sample.type }}</td>
                <td class="py-2 px-4 border-b">{{ sample.uploader }}</td>
                <td class="py-2 px-4 border-b">{{ sample.uploadedAt }}</td>
                <td class="py-2 px-4 border-b space-x-2">
                  <button class="text-blue-500 hover:underline" @click="showDetail(sample)">详情</button>
                  <button class="text-yellow-500 hover:underline" @click="editSample(sample)">编辑</button>
                  <button class="text-red-500 hover:underline" @click="confirmDelete(sample)">删除</button>
                </td>
              </tr>
              <tr v-if="pagedSamples.length === 0">
                <td colspan="6" class="text-center py-4 text-gray-400">暂无样本</td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- 样本网格视图（图片缩略图） -->
        <div v-else class="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div v-for="sample in pagedSamples" :key="sample.id" class="bg-white rounded shadow p-4 relative flex flex-col">
            <div class="flex items-center mb-2">
              <input type="checkbox" v-model="selectedSamples" :value="sample.id" class="mr-2" />
              <span class="font-bold text-blue-700">{{ sample.name }}</span>
            </div>
            <div v-if="sample.type==='图片'">
              <img :src="sample.url || '/public/placeholder.png'" class="w-full h-32 object-cover rounded mb-2" />
            </div>
            <div class="text-xs text-gray-500 mb-1">类型：{{ sample.type }}</div>
            <div class="text-xs text-gray-500 mb-1">上传者：{{ sample.uploader }}</div>
            <div class="text-xs text-gray-500 mb-1">上传时间：{{ sample.uploadedAt }}</div>
            <div class="flex items-center mt-2 space-x-2">
              <button @click="showDetail(sample)" class="text-blue-500 text-sm">详情</button>
              <button @click="editSample(sample)" class="text-yellow-500 text-sm">编辑</button>
              <button @click="confirmDelete(sample)" class="text-red-500 text-sm">删除</button>
            </div>
          </div>
        </div>
        <!-- 分页 -->
        <div class="flex justify-between items-center mt-4 text-sm">
          <div>共 {{ filteredSamples.length }} 条</div>
          <div class="space-x-2">
            <button class="px-2" :disabled="page===1" @click="page--">上一页</button>
            <span>{{ page }}</span>
            <button class="px-2" :disabled="page===maxPage" @click="page++">下一页</button>
          </div>
        </div>
        <!-- 新建/编辑弹窗表单 -->
        <div v-if="showAddForm || showEditForm" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-30 z-50">
          <div class="bg-white rounded-xl shadow-xl p-8 w-full max-w-2xl relative">
            <button class="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl" @click="closeForm">×</button>
            <h2 class="text-2xl font-bold mb-6 text-center">{{ showAddForm ? '新建样本集' : '编辑样本集' }}</h2>
            <form @submit.prevent="showAddForm ? addSample() : updateSample()">
              <div class="mb-4">
                <label class="block text-gray-600 mb-1">样本集名称</label>
                <input v-model="form.name" type="text" class="w-full px-3 py-2 border rounded" required />
              </div>
              <div class="mb-4">
                <label class="block text-gray-600 mb-1">数据集种类</label>
                <div class="flex space-x-2 mb-2">
                  <button v-for="tab in datasetTabs" :key="tab" type="button" @click="form.kind=tab" :class="form.kind===tab ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'" class="px-4 py-1 rounded">{{ tab }}</button>
                </div>
              </div>
              <div class="mb-4">
                <label class="block text-gray-600 mb-1">数据集类型</label>
                <div class="flex flex-wrap gap-2">
                  <div v-for="type in datasetTypes[form.kind]" :key="type.name" @click="form.type=type.name" :class="form.type===type.name ? 'border-blue-500' : 'border-gray-300'" class="border rounded p-2 flex flex-col items-center cursor-pointer w-28">
                    <img :src="type.icon" class="w-12 h-12 mb-1" />
                    <span>{{ type.name }}</span>
                  </div>
                </div>
              </div>
              <div class="mb-4 flex space-x-4">
                <div>
                  <label class="block text-gray-600 mb-1">版本</label>
                  <input v-model="form.version" type="number" min="1" class="w-20 px-2 py-1 border rounded" />
                </div>
                <div>
                  <label class="block text-gray-600 mb-1">标注方式</label>
                  <select v-model="form.annotation" class="px-2 py-1 border rounded">
                    <option value="内部标注">内部标注</option>
                    <option value="外部导入">外部导入</option>
                  </select>
                </div>
                <div>
                  <label class="block text-gray-600 mb-1">标签类别</label>
                  <input v-model="form.label" type="text" class="w-32 px-2 py-1 border rounded" placeholder="输入类别" />
                </div>
              </div>
              <div class="mb-4">
                <label class="block text-gray-600 mb-1">备注</label>
                <textarea v-model="form.remark" class="w-full px-3 py-2 border rounded" maxlength="512" placeholder="请输入内容" />
              </div>
              <div class="mb-4">
                <label class="block text-gray-600 mb-1">上传样本文件</label>
                <input type="file" ref="fileInput" multiple @change="handleFileChange" class="mb-2" />
                <div class="flex flex-wrap gap-2">
                  <div v-for="file in previewFiles" :key="file.name" class="w-20 h-20 border rounded flex items-center justify-center overflow-hidden">
                    <img v-if="file.type.startsWith('image')" :src="file.url" class="object-cover w-full h-full" />
                    <span v-else class="text-xs text-gray-400">{{ file.name }}</span>
                  </div>
                </div>
              </div>
              <div class="flex justify-end gap-4">
                <button type="button" class="px-6 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" @click="closeForm">取消</button>
                <button type="submit" class="px-6 py-2 rounded bg-blue-600 text-white hover:bg-blue-700">确定</button>
              </div>
            </form>
          </div>
        </div>
        <!-- 样本分布可视化弹窗 -->
        <div v-if="showDistChart" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-30 z-50">
          <div class="bg-white rounded-xl shadow-xl p-8 w-full max-w-2xl relative">
            <button class="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl" @click="showDistChart=false">×</button>
            <h2 class="text-2xl font-bold mb-6 text-center">样本分布</h2>
            <canvas ref="distChart" width="600" height="300"></canvas>
          </div>
        </div>
        <!-- 删除确认弹窗 -->
        <div v-if="showDeleteConfirm" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-30 z-50">
          <div class="bg-white rounded-xl shadow-xl p-8 w-full max-w-sm relative">
            <div class="text-lg mb-6">确定要删除样本 <span class="font-bold text-red-600">{{ deleteTarget?.name }}</span> 吗？</div>
            <div class="flex justify-end gap-4">
              <button class="px-6 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" @click="showDeleteConfirm=false">取消</button>
              <button class="px-6 py-2 rounded bg-red-600 text-white hover:bg-red-700" @click="deleteSampleConfirm">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { fetchSamples, fetchSampleInfo, uploadSample, deleteSample, getSampleInfo } from '@/api.js'
import { ElMessage, ElLoading } from 'element-plus'
// 样本分组树结构可本地静态
const sampleGroups = ref([
  { id: 1, name: '全部样本', children: [
    { id: 2, name: '文本样本' },
    { id: 3, name: '图片样本' },
    { id: 4, name: '音频样本' },
  ]}
])
const selectedGroup = ref(1)
const allSamples = ref([])
const searchName = ref('')
const searchUploader = ref('')
const searchType = ref('')
const page = ref(1)
const pageSize = 12
const showAddForm = ref(false)
const showEditForm = ref(false)
const showDeleteConfirm = ref(false)
const showDistChart = ref(false)
const deleteTarget = ref(null)
const form = ref({ id: null, name: '', kind: '图片', type: '', version: 1, annotation: '内部标注', label: '', remark: '' })
const fileInput = ref(null)
const previewFiles = ref([])
const selectedSamples = ref([])
const allSelected = ref(false)
const viewMode = ref('table')
const datasetTabs = ['图片', '文本', '音频', '视频', '其他']
const datasetTypes = {
  '图片': [
    { name: '图片分类', icon: '/public/img_classify.png' },
    { name: '目标检测', icon: '/public/obj_detect.png' },
    { name: '图像生成', icon: '/public/img_gen.png' },
    { name: '语义分割', icon: '/public/seg.png' },
    { name: '中文OCR', icon: '/public/ocr.png' },
    { name: '图像通用', icon: '/public/img_general.png' },
  ],
  '文本': [
    { name: '文本分类', icon: '/public/txt_classify.png' },
    { name: '命名实体', icon: '/public/ner.png' },
    { name: '文本情感分析', icon: '/public/sentiment.png' },
  ],
  '音频': [
    { name: '音频分类', icon: '/public/audio_classify.png' },
    { name: '语音识别', icon: '/public/asr.png' },
  ],
  '视频': [
    { name: '视频分类', icon: '/public/video_classify.png' },
  ],
  '其他': [
    { name: '其他', icon: '/public/other.png' },
  ]
}
const loading = ref(false)
const error = ref('')
const samples = ref([])
const distribution = ref([])

async function loadSamples() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetchSamples()
    samples.value = res.data.samples
  } catch (e) {
    error.value = '样本列表加载失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}
async function loadDistribution() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetchSampleInfo()
    distribution.value = res.data.distribution || []
  } catch (e) {
    error.value = '样本分布加载失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}
onMounted(() => {
  loadSamples()
})
const filteredSamples = computed(() => {
  return allSamples.value.filter(s => {
    return (
      (!searchName.value || s.name.includes(searchName.value)) &&
      (!searchUploader.value || s.uploader.includes(searchUploader.value)) &&
      (!searchType.value || s.type === searchType.value) &&
      (selectedGroup.value === 1 || s.type === sampleGroups.value[0].children.find(g => g.id === selectedGroup.value)?.name.replace('样本',''))
    )
  })
})
const maxPage = computed(() => Math.max(1, Math.ceil(filteredSamples.value.length / pageSize)))
const pagedSamples = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredSamples.value.slice(start, start + pageSize)
})
function filterSamples() {
  page.value = 1
}
function resetFilters() {
  searchName.value = ''
  searchUploader.value = ''
  searchType.value = ''
  page.value = 1
}
function selectGroup(id) {
  selectedGroup.value = id
  page.value = 1
}
function closeForm() {
  showAddForm.value = false
  showEditForm.value = false
  form.value = { id: null, name: '', kind: '图片', type: '', version: 1, annotation: '内部标注', label: '', remark: '' }
  previewFiles.value = []
}
// 上传样本
async function handleFileChange(e) {
  const files = Array.from(e.target.files)
  previewFiles.value = files.map(f => {
    const url = f.type.startsWith('image') ? URL.createObjectURL(f) : ''
    return { name: f.name, type: f.type, url }
  })
  form.value.files = files
}
async function addSample() {
  if (!form.value.name || !form.value.type) return
  const formData = new FormData()
  formData.append('name', form.value.name)
  formData.append('kind', form.value.kind)
  formData.append('type', form.value.type)
  formData.append('version', form.value.version)
  formData.append('annotation', form.value.annotation)
  formData.append('label', form.value.label)
  formData.append('remark', form.value.remark)
  if (form.value.files) {
    for (const file of form.value.files) {
      formData.append('files', file)
    }
  }
  try {
    await uploadSample(formData)
    await loadSamples()
    closeForm()
    alert('上传成功')
  } catch (err) {
    alert('上传失败')
  }
}
// 删除样本
async function deleteSampleConfirm() {
  if (!deleteTarget.value) return
  try {
    await deleteSample(deleteTarget.value.id)
    await loadSamples()
    showDeleteConfirm.value = false
    deleteTarget.value = null
    alert('样本删除成功')
  } catch (err) {
    alert('样本删除失败')
  }
}
function confirmDelete(sample) {
  deleteTarget.value = sample
  showDeleteConfirm.value = true
}
function editSample(sample) {
  form.value = { ...sample }
  showEditForm.value = true
}
function updateSample() {
  // 可扩展：实现样本信息编辑接口
  closeForm()
}
function showDetail(sample) {
  alert('样本详情：' + sample.name)
}
function toggleAll(e) {
  allSelected.value = e.target.checked
  selectedSamples.value = allSelected.value ? pagedSamples.value.map(f => f.id) : []
}
// 样本分布可视化
const distChart = ref(null)
watch(showDistChart, (v) => {
  if (v) {
    loadDistribution()
    setTimeout(drawDistChart, 100)
  }
})
function drawDistChart() {
  if (!distChart.value) return
  const ctx = distChart.value.getContext('2d')
  ctx.clearRect(0,0,600,300)
  
  // 使用真实数据，如果没有则使用默认数据
  const realData = distribution.value.length > 0 ? distribution.value : [
    { type: '图片分类', count: 8 },
    { type: '目标检测', count: 40 },
    { type: '图像生成', count: 10 },
    { type: '语义分割', count: 12 },
    { type: '中文OCR', count: 2 },
    { type: '文本分类', count: 7 },
    { type: '音频分类', count: 6 },
    { type: '语音识别', count: 1 }
  ]
  
  const data = realData.map(item => item.count)
  const labels = realData.map(item => item.type)
  const colors = ['#3b82f6','#06b6d4','#6366f1','#10b981','#f59e42','#f43f5e','#a78bfa','#fbbf24']
  const max = Math.max(...data)
  
  for(let i=0;i<data.length;i++){
    ctx.fillStyle = colors[i % colors.length]
    ctx.fillRect(60+i*60, 280-data[i]/max*220, 40, data[i]/max*220)
    ctx.fillStyle = '#222'
    ctx.fillText(labels[i], 60+i*60, 295)
    ctx.fillText(data[i], 75+i*60, 270-data[i]/max*220)
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
</script> 