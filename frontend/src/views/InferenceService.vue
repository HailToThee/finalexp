<template>
  <div class="flex min-h-screen bg-gray-50">
    <!-- 左侧树形导航 -->
    <div class="w-64 bg-white shadow-lg rounded-r-2xl p-6 mr-8 mt-8 h-fit">
      <div class="font-bold text-lg mb-4">服务分组</div>
      <ul>
        <li :class="['cursor-pointer px-3 py-2 rounded mb-1', selectedGroup===1 ? 'bg-blue-100 text-blue-600 font-bold' : 'hover:bg-gray-100']" @click="selectGroup(1)">全部服务</li>
        <li v-for="g in serviceGroups[0].children" :key="g.id" :class="['cursor-pointer px-3 py-2 rounded mb-1', selectedGroup===g.id ? 'bg-blue-100 text-blue-600 font-bold' : 'hover:bg-gray-100']" @click="selectGroup(g.id)">{{ g.name }}</li>
      </ul>
    </div>
    <!-- 主内容区 -->
    <div class="flex-1 max-w-6xl mx-auto p-8">
      <div class="bg-white rounded-xl shadow p-8">
        <!-- 顶部筛选 -->
        <div class="flex items-center mb-6 justify-between">
          <div class="flex space-x-2">
            <input v-model="searchName" type="text" placeholder="服务名" class="border rounded px-3 py-2 focus:outline-none focus:ring w-48" />
            <input v-model="searchCreator" type="text" placeholder="创建人" class="border rounded px-3 py-2 focus:outline-none focus:ring w-32" />
            <select v-model="searchType" class="border rounded px-3 py-2 focus:outline-none focus:ring w-32">
              <option value="">全部类型</option>
              <option value="文本">文本</option>
              <option value="图片">图片</option>
              <option value="音频">音频</option>
            </select>
            <select v-model="searchStatus" class="border rounded px-3 py-2 focus:outline-none focus:ring w-32">
              <option value="">全部状态</option>
              <option value="运行中">运行中</option>
              <option value="已停止">已停止</option>
            </select>
            <button @click="filterServices" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">查询</button>
            <button @click="resetFilters" class="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300">重置</button>
          </div>
          <button @click="showAddForm=true" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">+ 新建服务</button>
        </div>
        <!-- 服务表格 -->
        <div class="bg-gray-50 rounded-lg shadow-inner p-4">
          <table class="min-w-full text-sm">
            <thead class="bg-gray-100">
              <tr>
                <th class="py-2 px-4 border-b">服务名</th>
                <th class="py-2 px-4 border-b">类型</th>
                <th class="py-2 px-4 border-b">状态</th>
                <th class="py-2 px-4 border-b">创建人</th>
                <th class="py-2 px-4 border-b">创建时间</th>
                <th class="py-2 px-4 border-b">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="service in pagedServices" :key="service.id" class="hover:bg-blue-50">
                <td class="py-2 px-4 border-b">{{ service.name }}</td>
                <td class="py-2 px-4 border-b">{{ service.type }}</td>
                <td class="py-2 px-4 border-b">
                  <span :class="service.status==='运行中' ? 'text-green-600 font-bold' : 'text-gray-400'">{{ service.status }}</span>
                </td>
                <td class="py-2 px-4 border-b">{{ service.creator }}</td>
                <td class="py-2 px-4 border-b">{{ service.createdAt }}</td>
                <td class="py-2 px-4 border-b space-x-2">
                  <button class="text-blue-500 hover:underline" @click="showDetail(service)">详情</button>
                  <button class="text-yellow-500 hover:underline" @click="editService(service)">编辑</button>
                  <button class="text-red-500 hover:underline" @click="confirmDelete(service)">删除</button>
                </td>
              </tr>
              <tr v-if="pagedServices.length === 0">
                <td colspan="6" class="text-center py-4 text-gray-400">暂无服务</td>
              </tr>
            </tbody>
          </table>
          <div class="flex justify-between items-center mt-4 text-sm">
            <div>共 {{ filteredServices.length }} 条</div>
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
            <h2 class="text-2xl font-bold mb-6 text-center">{{ showAddForm ? '新建服务' : '编辑服务' }}</h2>
            <form @submit.prevent="showAddForm ? addServiceData() : updateService()">
              <div class="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label class="block text-gray-600 mb-1">服务名</label>
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
                  <label class="block text-gray-600 mb-1">状态</label>
                  <select v-model="form.status" class="w-full px-3 py-2 border rounded" required>
                    <option value="">请选择</option>
                    <option value="运行中">运行中</option>
                    <option value="已停止">已停止</option>
                  </select>
                </div>
                <div>
                  <label class="block text-gray-600 mb-1">创建人</label>
                  <input v-model="form.creator" type="text" class="w-full px-3 py-2 border rounded" required />
                </div>
                <div>
                  <label class="block text-gray-600 mb-1">创建时间</label>
                  <input v-model="form.createdAt" type="datetime-local" class="w-full px-3 py-2 border rounded" required />
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
            <div class="text-lg mb-6">确定要删除服务 <span class="font-bold text-red-600">{{ deleteTarget?.name }}</span> 吗？</div>
            <div class="flex justify-end gap-4">
              <button class="px-6 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" @click="showDeleteConfirm=false">取消</button>
              <button class="px-6 py-2 rounded bg-red-600 text-white hover:bg-red-700" @click="deleteServiceConfirm">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchServices, addService, deleteService, getInferenceResult } from '@/api.js'
// 服务分组树结构可本地静态
const serviceGroups = ref([
  { id: 1, name: '全部服务', children: [
    { id: 2, name: '文本推理' },
    { id: 3, name: '图像推理' },
    { id: 4, name: '音频推理' },
  ]}
])
const selectedGroup = ref(1)
const allServices = ref([])
const searchName = ref('')
const searchCreator = ref('')
const searchType = ref('')
const searchStatus = ref('')
const page = ref(1)
const pageSize = 10
const showAddForm = ref(false)
const showEditForm = ref(false)
const showDeleteConfirm = ref(false)
const deleteTarget = ref(null)
const form = ref({ id: null, name: '', type: '', status: '', creator: '', createdAt: '' })

// 获取服务列表
async function fetchServicesData() {
  try {
    const res = await fetchServices()
    allServices.value = res.data.services || []
  } catch (e) {
    allServices.value = []
  }
}

onMounted(() => {
  fetchServicesData()
})

const filteredServices = computed(() => {
  return allServices.value.filter(s => {
    return (
      (!searchName.value || s.name.includes(searchName.value)) &&
      (!searchCreator.value || s.creator.includes(searchCreator.value)) &&
      (!searchType.value || s.type === searchType.value) &&
      (!searchStatus.value || s.status === searchStatus.value) &&
      (selectedGroup.value === 1 || s.type === serviceGroups.value[0].children.find(g => g.id === selectedGroup.value)?.name.replace('推理',''))
    )
  })
})
const maxPage = computed(() => Math.max(1, Math.ceil(filteredServices.value.length / pageSize)))
const pagedServices = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredServices.value.slice(start, start + pageSize)
})
function filterServices() {
  page.value = 1
}
function resetFilters() {
  searchName.value = ''
  searchCreator.value = ''
  searchType.value = ''
  searchStatus.value = ''
  page.value = 1
}
function selectGroup(id) {
  selectedGroup.value = id
  page.value = 1
}
function closeForm() {
  showAddForm.value = false
  showEditForm.value = false
  form.value = { id: null, name: '', type: '', status: '', creator: '', createdAt: '' }
}
// 新建服务
async function addServiceData() {
  // 这里只做简单示例，实际可根据表单内容构造请求体
  try {
    await addService(form.value)
    await fetchServicesData()
    showAddForm.value = false
    closeForm()
    alert('新建服务成功')
  } catch (err) {
    alert('新建服务失败')
  }
}
// 删除服务
async function deleteServiceConfirm() {
  if (!deleteTarget.value) return
  try {
    await deleteService(deleteTarget.value.id)
    await fetchServicesData()
    showDeleteConfirm.value = false
    deleteTarget.value = null
  } catch (err) {
    alert('删除失败')
  }
}
function confirmDelete(service) {
  deleteTarget.value = service
  showDeleteConfirm.value = true
}
function editService(service) {
  form.value = { ...service }
  showEditForm.value = true
}
function updateService() {
  // 可扩展：实现服务信息编辑接口
  closeForm()
}
function showDetail(service) {
  alert('服务详情：' + service.name)
}
// 获取推理结果
async function showResult(service) {
  try {
    const res = await getInferenceResult(service.id)
    // 处理推理结果
    console.log('推理结果:', res.data)
    alert('推理结果获取成功')
  } catch (err) {
    alert('获取推理结果失败')
  }
}
</script> 