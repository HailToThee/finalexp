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
        <!-- 顶部筛选 -->
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
          <button @click="showAddForm=true" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">+ 新增样本</button>
        </div>
        <!-- 样本表格 -->
        <div class="bg-gray-50 rounded-lg shadow-inner p-4">
          <table class="min-w-full text-sm">
            <thead class="bg-gray-100">
              <tr>
                <th class="py-2 px-4 border-b">样本名</th>
                <th class="py-2 px-4 border-b">类型</th>
                <th class="py-2 px-4 border-b">上传人</th>
                <th class="py-2 px-4 border-b">上传时间</th>
                <th class="py-2 px-4 border-b">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="sample in pagedSamples" :key="sample.id" class="hover:bg-blue-50">
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
                <td colspan="5" class="text-center py-4 text-gray-400">暂无样本</td>
              </tr>
            </tbody>
          </table>
          <div class="flex justify-between items-center mt-4 text-sm">
            <div>共 {{ filteredSamples.length }} 条</div>
            <div class="space-x-2">
              <button class="px-2" :disabled="page===1" @click="page--">上一页</button>
              <span>{{ page }}</span>
              <button class="px-2" :disabled="page===maxPage" @click="page++">下一页</button>
            </div>
          </div>
        </div>
        <!-- 新增/编辑弹窗表单 -->
        <div v-if="showAddForm || showEditForm" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-30 z-50">
          <div class="bg-white rounded-xl shadow-xl p-8 w-full max-w-xl relative">
            <button class="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl" @click="closeForm">×</button>
            <h2 class="text-2xl font-bold mb-6 text-center">{{ showAddForm ? '新增样本' : '编辑样本' }}</h2>
            <form @submit.prevent="showAddForm ? addSample() : updateSample()">
              <div class="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label class="block text-gray-600 mb-1">样本名</label>
                  <input v-model="form.name" type="text" class="w-full px-3 py-2 border rounded" required />
                </div>
                <div>
                  <label class="block text-gray-600 mb-1">类型</label>
                  <select v-model="form.type" class="w-full px-3 py-2 border rounded" required>
                    <option value="">请选择</option>
                    <option value="文本">文本</option>
                    <option value="图片">图片</option>
                    <option value="音频">音频</option>
                  </select>
                </div>
                <div>
                  <label class="block text-gray-600 mb-1">上传人</label>
                  <input v-model="form.uploader" type="text" class="w-full px-3 py-2 border rounded" required />
                </div>
                <div>
                  <label class="block text-gray-600 mb-1">上传时间</label>
                  <input v-model="form.uploadedAt" type="datetime-local" class="w-full px-3 py-2 border rounded" required />
                </div>
              </div>
              <div class="flex justify-end gap-4">
                <button type="button" class="px-6 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" @click="closeForm">取消</button>
                <button type="submit" class="px-6 py-2 rounded bg-blue-600 text-white hover:bg-blue-700">确定</button>
              </div>
            </form>
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
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
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
const pageSize = 10
const showAddForm = ref(false)
const showEditForm = ref(false)
const showDeleteConfirm = ref(false)
const deleteTarget = ref(null)
const form = ref({ id: null, name: '', type: '', uploader: '', uploadedAt: '' })
const fileInput = ref(null)

// 获取样本列表
async function fetchSamples() {
  try {
    const res = await axios.get('/api/sample/list')
    allSamples.value = res.data.samples || []
  } catch (e) {
    allSamples.value = []
  }
}
onMounted(() => {
  fetchSamples()
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
  form.value = { id: null, name: '', type: '', uploader: '', uploadedAt: '' }
}
// 上传样本
async function handleFileChange(e) {
  const fileList = e.target.files
  if (fileList.length > 0) {
    const file = fileList[0]
    const formData = new FormData()
    formData.append('file', file)
    try {
      await axios.post('/api/sample/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      await fetchSamples()
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
    await axios.delete(`/api/sample/${deleteTarget.value.id}`)
    await fetchSamples()
    showDeleteConfirm.value = false
    deleteTarget.value = null
  } catch (err) {
    alert('删除失败')
  }
}
function confirmDelete(sample) {
  deleteTarget.value = sample
  showDeleteConfirm.value = true
}
function addSample() {
  fileInput.value.click()
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
</script> 