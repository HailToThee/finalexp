<template>
    <div class="p-8 bg-gray-50 min-h-screen">
        <div class="max-w-6xl mx-auto">
            <div class="bg-white rounded-xl shadow p-8">
                <div class="flex items-center mb-6 justify-between">
                    <div class="flex space-x-2">
                        <input v-model="searchName" type="text" placeholder="请输入模型名称" class="border rounded px-3 py-2 focus:outline-none focus:ring w-48" />
                        <input v-model="searchUploader" type="text" placeholder="上传人" class="border rounded px-3 py-2 focus:outline-none focus:ring w-32" />
                        <input v-model="searchDate" type="date" class="border rounded px-3 py-2 focus:outline-none focus:ring w-36" />
                        <button @click="filterModels" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">查询</button>
                        <button @click="resetFilters" class="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300">重置</button>
                    </div>
                    <div>
                        <button @click="showAddForm=true" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">+ 新增模型</button>
                        <input type="file" ref="fileInput" class="hidden" @change="handleFileChange" />
                    </div>
                </div>
                <div class="bg-gray-50 rounded-lg shadow-inner p-4">
                    <table class="min-w-full text-sm">
                        <thead class="bg-gray-100">
                            <tr>
                                <th class="py-2 px-4 border-b">模型名称</th>
                                <th class="py-2 px-4 border-b">上传人</th>
                                <th class="py-2 px-4 border-b">上传时间</th>
                                <th class="py-2 px-4 border-b">状态</th>
                                <th class="py-2 px-4 border-b">操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="model in pagedModels" :key="model.id" class="hover:bg-blue-50">
                                <td class="py-2 px-4 border-b">{{ model.name }}</td>
                                <td class="py-2 px-4 border-b">{{ model.uploader }}</td>
                                <td class="py-2 px-4 border-b">{{ model.uploadedAt }}</td>
                                <td class="py-2 px-4 border-b">
                                    <span class="inline-block w-2 h-2 rounded-full mr-2" :class="model.status === '已部署' ? 'bg-green-500' : 'bg-gray-400'"></span>
                                    {{ model.status }}
                                </td>
                                <td class="py-2 px-4 border-b space-x-2">
                                    <button class="text-blue-500 hover:underline" @click="showDetail(model)">详情</button>
                                    <button class="text-yellow-500 hover:underline" @click="editModel(model)">编辑</button>
                                    <button class="text-red-500 hover:underline" @click="confirmDelete(model)">删除</button>
                                </td>
                            </tr>
                            <tr v-if="pagedModels.length === 0">
                                <td colspan="5" class="text-center py-4 text-gray-400">暂无模型</td>
                            </tr>
                        </tbody>
                    </table>
                    <div class="flex justify-between items-center mt-4 text-sm">
                        <div>共 {{ filteredModels.length }} 条</div>
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
                        <h2 class="text-2xl font-bold mb-6 text-center">{{ showAddForm ? '新增模型' : '编辑模型' }}</h2>
                        <form @submit.prevent="showAddForm ? addModel() : updateModel()">
                            <div class="grid grid-cols-2 gap-4 mb-4">
                                <div>
                                    <label class="block text-gray-600 mb-1">模型名称</label>
                                    <input v-model="form.name" type="text" class="w-full px-3 py-2 border rounded" required />
                                </div>
                                <div>
                                    <label class="block text-gray-600 mb-1">上传人</label>
                                    <input v-model="form.uploader" type="text" class="w-full px-3 py-2 border rounded" required />
                                </div>
                                <div>
                                    <label class="block text-gray-600 mb-1">上传时间</label>
                                    <input v-model="form.uploadedAt" type="datetime-local" class="w-full px-3 py-2 border rounded" required />
                                </div>
                                <div>
                                    <label class="block text-gray-600 mb-1">状态</label>
                                    <select v-model="form.status" class="w-full px-3 py-2 border rounded">
                                        <option value="已部署">已部署</option>
                                        <option value="未部署">未部署</option>
                                    </select>
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
                        <div class="text-lg mb-6">确定要删除模型 <span class="font-bold text-red-600">{{ deleteTarget?.name }}</span> 吗？</div>
                        <div class="flex justify-end gap-4">
                            <button class="px-6 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" @click="showDeleteConfirm=false">取消</button>
                            <button class="px-6 py-2 rounded bg-red-600 text-white hover:bg-red-700" @click="deleteModelConfirm">删除</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, computed } from 'vue'
const allModels = ref([
    // 示例数据，后续可对接后端API
    { id: 1, name: 'ResNet50', uploader: '张三', uploadedAt: '2024-06-01T10:00', status: '已部署' },
    { id: 2, name: 'BERT-Base', uploader: '李四', uploadedAt: '2024-06-02T14:30', status: '未部署' },
])
const searchName = ref('')
const searchUploader = ref('')
const searchDate = ref('')
const page = ref(1)
const pageSize = 10
const showAddForm = ref(false)
const showEditForm = ref(false)
const showDeleteConfirm = ref(false)
const deleteTarget = ref(null)
const form = ref({ id: null, name: '', uploader: '', uploadedAt: '', status: '已部署' })
const filteredModels = computed(() => {
    return allModels.value.filter(m => {
        return (
            (!searchName.value || m.name.includes(searchName.value)) &&
            (!searchUploader.value || m.uploader.includes(searchUploader.value)) &&
            (!searchDate.value || m.uploadedAt.startsWith(searchDate.value))
        )
    })
})
const maxPage = computed(() => Math.max(1, Math.ceil(filteredModels.value.length / pageSize)))
const pagedModels = computed(() => {
    const start = (page.value - 1) * pageSize
    return filteredModels.value.slice(start, start + pageSize)
})
function filterModels() {
    page.value = 1
}
function resetFilters() {
    searchName.value = ''
    searchUploader.value = ''
    searchDate.value = ''
    page.value = 1
}
function closeForm() {
    showAddForm.value = false
    showEditForm.value = false
    form.value = { id: null, name: '', uploader: '', uploadedAt: '', status: '已部署' }
}
function addModel() {
    const newId = allModels.value.length ? Math.max(...allModels.value.map(m => m.id)) + 1 : 1
    allModels.value.push({ ...form.value, id: newId })
    closeForm()
}
function editModel(model) {
    form.value = { ...model }
    showEditForm.value = true
}
function updateModel() {
    const idx = allModels.value.findIndex(m => m.id === form.value.id)
    if (idx !== -1) allModels.value[idx] = { ...form.value }
    closeForm()
}
function confirmDelete(model) {
    deleteTarget.value = model
    showDeleteConfirm.value = true
}
function deleteModelConfirm() {
    allModels.value.splice(allModels.value.findIndex(m => m.id === deleteTarget.value.id), 1)
    showDeleteConfirm.value = false
    deleteTarget.value = null
}
function showDetail(model) {
    alert('模型详情：' + model.name)
}
const fileInput = ref(null)
function handleFileChange(e) {
    const file = e.target.files[0]
    if (file) {
        // 这里可添加上传逻辑
        alert('模拟上传: ' + file.name)
    }
}
</script>