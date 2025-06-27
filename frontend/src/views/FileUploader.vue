<template>
    <div class="p-8 bg-gray-50 min-h-screen">
        <div class="max-w-6xl mx-auto">
            <div class="bg-white rounded-xl shadow p-8">
                <div class="flex items-center mb-6 justify-between">
                    <div class="flex space-x-2">
                        <input v-model="searchName" type="text" placeholder="请输入文件名" class="border rounded px-3 py-2 focus:outline-none focus:ring w-48" />
                        <input v-model="searchUploader" type="text" placeholder="上传人" class="border rounded px-3 py-2 focus:outline-none focus:ring w-32" />
                        <input v-model="searchDate" type="date" class="border rounded px-3 py-2 focus:outline-none focus:ring w-36" />
                        <button @click="filterFiles" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">查询</button>
                        <button @click="resetFilters" class="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300">重置</button>
                    </div>
                    <div>
                        <button @click="showAddForm=true" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">+ 上传文件</button>
                        <input type="file" ref="fileInput" class="hidden" multiple @change="handleFileChange" />
                    </div>
                </div>
                <div class="bg-gray-50 rounded-lg shadow-inner p-4">
                    <table class="min-w-full text-sm">
                        <thead class="bg-gray-100">
                            <tr>
                                <th class="py-2 px-4 border-b">文件名</th>
                                <th class="py-2 px-4 border-b">上传人</th>
                                <th class="py-2 px-4 border-b">上传时间</th>
                                <th class="py-2 px-4 border-b">操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="file in pagedFiles" :key="file.id" class="hover:bg-blue-50">
                                <td class="py-2 px-4 border-b">{{ file.name }}</td>
                                <td class="py-2 px-4 border-b">{{ file.uploader }}</td>
                                <td class="py-2 px-4 border-b">{{ file.uploadedAt }}</td>
                                <td class="py-2 px-4 border-b space-x-2">
                                    <button class="text-blue-500 hover:underline" @click="showDetail(file)">详情</button>
                                    <button class="text-yellow-500 hover:underline" @click="editFile(file)">编辑</button>
                                    <button class="text-red-500 hover:underline" @click="confirmDelete(file)">删除</button>
                                    <button class="text-gray-500 hover:underline" @click="downloadFile(file)">下载</button>
                                </td>
                            </tr>
                            <tr v-if="pagedFiles.length === 0">
                                <td colspan="4" class="text-center py-4 text-gray-400">暂无文件</td>
                            </tr>
                        </tbody>
                    </table>
                    <div class="flex justify-between items-center mt-4 text-sm">
                        <div>共 {{ filteredFiles.length }} 条</div>
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
                        <h2 class="text-2xl font-bold mb-6 text-center">{{ showAddForm ? '上传文件' : '编辑文件' }}</h2>
                        <form @submit.prevent="showAddForm ? addFile() : updateFile()">
                            <div class="grid grid-cols-2 gap-4 mb-4">
                                <div>
                                    <label class="block text-gray-600 mb-1">文件名</label>
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
                        <div class="text-lg mb-6">确定要删除文件 <span class="font-bold text-red-600">{{ deleteTarget?.name }}</span> 吗？</div>
                        <div class="flex justify-end gap-4">
                            <button class="px-6 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" @click="showDeleteConfirm=false">取消</button>
                            <button class="px-6 py-2 rounded bg-red-600 text-white hover:bg-red-700" @click="deleteFileConfirm">删除</button>
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

const allFiles = ref([])
const searchName = ref('')
const searchUploader = ref('')
const searchDate = ref('')
const page = ref(1)
const pageSize = 10
const showAddForm = ref(false)
const showEditForm = ref(false)
const showDeleteConfirm = ref(false)
const deleteTarget = ref(null)
const form = ref({ id: null, name: '', uploader: '', uploadedAt: '' })
const fileInput = ref(null)

// 获取文件列表
async function fetchFiles() {
    try {
        const res = await axios.get('/api/file/list')
        allFiles.value = res.data.files || []
    } catch (e) {
        allFiles.value = []
    }
}

onMounted(() => {
    fetchFiles()
})

const filteredFiles = computed(() => {
    return allFiles.value.filter(f => {
        return (
            (!searchName.value || f.name.includes(searchName.value)) &&
            (!searchUploader.value || f.uploader.includes(searchUploader.value)) &&
            (!searchDate.value || f.uploadedAt.startsWith(searchDate.value))
        )
    })
})
const maxPage = computed(() => Math.max(1, Math.ceil(filteredFiles.value.length / pageSize)))
const pagedFiles = computed(() => {
    const start = (page.value - 1) * pageSize
    return filteredFiles.value.slice(start, start + pageSize)
})
function filterFiles() {
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
    form.value = { id: null, name: '', uploader: '', uploadedAt: '' }
}
// 上传文件
async function handleFileChange(e) {
    const fileList = e.target.files
    if (fileList.length > 0) {
        const file = fileList[0]
        const formData = new FormData()
        formData.append('file', file)
        try {
            await axios.post('/api/file/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
            await fetchFiles()
            alert('上传成功')
        } catch (err) {
            alert('上传失败')
        }
    }
}
// 删除文件
async function deleteFileConfirm() {
    if (!deleteTarget.value) return
    try {
        await axios.delete(`/api/file/${deleteTarget.value.id}`)
        await fetchFiles()
        showDeleteConfirm.value = false
        deleteTarget.value = null
    } catch (err) {
        alert('删除失败')
    }
}
function confirmDelete(file) {
    deleteTarget.value = file
    showDeleteConfirm.value = true
}
// 下载文件
async function downloadFile(file) {
    try {
        const res = await axios.get(`/api/file/download/${file.id}`, { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([res.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', file.name)
        document.body.appendChild(link)
        link.click()
        link.remove()
    } catch (err) {
        alert('下载失败')
    }
}
function addFile() {
    fileInput.value.click()
}
function editFile(file) {
    form.value = { ...file }
    showEditForm.value = true
}
function updateFile() {
    // 可扩展：实现文件信息编辑接口
    closeForm()
}
function showDetail(file) {
    alert('文件详情：' + file.name)
}
</script>