<template>
    <div class="min-h-screen bg-gray-100">
        <div class="container mx-auto p-6">
            <div class="bg-white rounded-lg shadow-lg p-6">
                <div class="flex justify-between items-center mb-6">
                    <h1 class="text-2xl font-bold text-gray-800">文件管理系统</h1>
                    <div class="flex space-x-2">
                        <button @click="showCreateFolderDialog=true" class="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600">+ 创建文件夹</button>
                        <button @click="showAddForm=true" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">+ 上传文件</button>
                        <input type="file" ref="fileInput" class="hidden" multiple @change="handleFileChange" />
                    </div>
                </div>

                <!-- 搜索和过滤 -->
                <div class="mb-4 flex space-x-4">
                    <input v-model="searchName" placeholder="搜索文件名..." class="border px-3 py-2 rounded flex-1" />
                    <input v-model="searchUploader" placeholder="搜索上传者..." class="border px-3 py-2 rounded flex-1" />
                    <input v-model="searchDate" type="date" class="border px-3 py-2 rounded" />
                    <button @click="filterFiles" class="bg-blue-500 text-white px-4 py-2 rounded">搜索</button>
                    <button @click="resetFilters" class="bg-gray-500 text-white px-4 py-2 rounded">重置</button>
                </div>

                <!-- 操作按钮 -->
                <div class="mb-4 flex items-center space-x-2">
                    <button @click="uploadFiles" class="bg-blue-500 text-white px-4 py-1 rounded">上传文件（断点续传）</button>
                    <button @click="batchDeleteData" :disabled="!selectedFiles.length" class="bg-red-500 text-white px-4 py-1 rounded">批量删除</button>
                    <button @click="batchDownloadData" :disabled="!selectedFiles.length" class="bg-blue-500 text-white px-4 py-1 rounded">批量下载</button>
                    <button @click="decompressDialog=true" :disabled="!selectedFiles.length" class="bg-yellow-500 text-white px-4 py-1 rounded">批量解压</button>
                    <button @click="viewMode='table'" :class="viewMode==='table' ? 'bg-gray-800 text-white' : 'bg-gray-200'" class="px-3 py-1 rounded">表格视图</button>
                    <button @click="viewMode='grid'" :class="viewMode==='grid' ? 'bg-gray-800 text-white' : 'bg-gray-200'" class="px-3 py-1 rounded">网格视图</button>
                    <button @click="viewMode='tree'" :class="viewMode==='tree' ? 'bg-gray-800 text-white' : 'bg-gray-200'" class="px-3 py-1 rounded">树形视图</button>
                </div>

                <!-- 树形视图 -->
                <div v-if="viewMode==='tree'" class="border rounded-lg">
                    <div class="bg-gray-50 p-4 border-b">
                        <div class="flex items-center">
                            <input type="checkbox" @change="toggleAll" :checked="allSelected" class="mr-3" />
                            <span class="font-semibold">文件结构</span>
                        </div>
                    </div>
                    <div class="p-4">
                        <!-- 默认文件夹 -->
                        <div class="space-y-1">
                            <div class="flex items-center hover:bg-gray-50 p-2 rounded">
                                <input type="checkbox" v-model="selectedFiles" :value="'folder_default'" class="mr-3" />
                                <button @click="toggleFolder('default')" class="flex items-center text-blue-600 hover:text-blue-800">
                                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V7a2 2 0 00-2-2h-7l-2-2H5a2 2 0 00-2 2z"/>
                                    </svg>
                                    <span class="font-medium">默认文件夹</span>
                                    <svg v-if="!expandedFolders.default" class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                                    </svg>
                                    <svg v-else class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                                    </svg>
                                </button>
                                <div class="ml-auto flex space-x-2">
                                    <button @click="showRenameDialog({isFolder: true, name: '默认文件夹', folderId: 'default'})" class="text-yellow-500 hover:text-yellow-700">重命名</button>
                                </div>
                            </div>
                            
                            <!-- 默认文件夹下的文件 -->
                            <div v-if="expandedFolders.default" class="ml-6 space-y-1">
                                <div v-for="file in getFilesInFolder(null)" :key="file.id" class="flex items-center hover:bg-gray-50 p-2 rounded">
                                    <input type="checkbox" v-model="selectedFiles" :value="file.id" class="mr-3" />
                                    <div class="flex items-center flex-1">
                                        <svg class="w-5 h-5 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v2a2 2 0 002 2h8a2 2 0 002-2v-2M4 12V8a2 2 0 012-2h8a2 2 0 012 2v4M4 12h16M4 12v4m16-4v4"/>
                                        </svg>
                                        <span class="flex-1">{{ file.name }}</span>
                                        <span class="text-sm text-gray-500 mr-4">{{ file.size }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 其他文件夹（兄弟关系） -->
                        <div v-for="folder in getFoldersInFolder(null)" :key="folder.id" class="space-y-1 mt-4">
                            <div class="flex items-center hover:bg-gray-50 p-2 rounded">
                                <input type="checkbox" v-model="selectedFiles" :value="`folder_${folder.realFolderId}`" class="mr-3" />
                                <button @click="toggleFolder(folder.realFolderId)" class="flex items-center text-blue-600 hover:text-blue-800">
                                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V7a2 2 0 00-2-2h-7l-2-2H5a2 2 0 00-2 2z"/>
                                    </svg>
                                    <span>{{ folder.name }}</span>
                                    <svg v-if="!expandedFolders[folder.realFolderId]" class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                                    </svg>
                                    <svg v-else class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                                    </svg>
                                </button>
                                <div class="ml-auto flex space-x-2">
                                    <button @click="showRenameDialog(folder)" class="text-yellow-500 hover:text-yellow-700">重命名</button>
                                    <button @click="confirmDelete(folder)" class="text-red-500 hover:text-red-700">删除</button>
                                </div>
                            </div>
                            
                            <!-- 文件夹下的文件 -->
                            <div v-if="expandedFolders[folder.realFolderId]" class="ml-6 space-y-1">
                                <div v-for="file in getFilesInFolder(folder.realFolderId)" :key="file.id" class="flex items-center hover:bg-gray-50 p-2 rounded">
                                    <input type="checkbox" v-model="selectedFiles" :value="file.id" class="mr-3" />
                                    <div class="flex items-center flex-1">
                                        <svg class="w-5 h-5 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v2a2 2 0 002 2h8a2 2 0 002-2v-2M4 12V8a2 2 0 012-2h8a2 2 0 012 2v4M4 12h16M4 12v4m16-4v4"/>
                                        </svg>
                                        <span class="flex-1">{{ file.name }}</span>
                                        <span class="text-sm text-gray-500 mr-4">{{ file.size }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 表格视图 -->
                <div v-else-if="viewMode==='table'" class="border rounded-lg">
                    <table class="min-w-full text-sm">
                        <thead class="bg-gray-100">
                            <tr>
                                <th class="py-2 px-4 border-b"><input type="checkbox" @change="toggleAll" :checked="allSelected" /></th>
                                <th class="py-2 px-4 border-b">名称</th>
                                <th class="py-2 px-4 border-b">大小</th>
                                <th class="py-2 px-4 border-b">类型</th>
                                <th class="py-2 px-4 border-b">时间</th>
                                <th class="py-2 px-4 border-b">操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="file in pagedFiles" :key="file.id" class="hover:bg-blue-50">
                                <td class="py-2 px-4 border-b"><input type="checkbox" v-model="selectedFiles" :value="file.id" /></td>
                                <td class="py-2 px-4 border-b flex items-center">
                                    <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v2a2 2 0 002 2h8a2 2 0 002-2v-2M4 12V8a2 2 0 012-2h8a2 2 0 012 2v4M4 12h16M4 12v4m16-4v4"/></svg>
                                    {{ file.name }}
                                </td>
                                <td class="py-2 px-4 border-b">{{ file.size }}</td>
                                <td class="py-2 px-4 border-b">{{ file.type }}</td>
                                <td class="py-2 px-4 border-b">{{ file.time }}</td>
                                <td class="py-2 px-4 border-b space-x-2">
                                    <button @click="downloadFileData(file)" class="text-green-500">下载</button>
                                    <button @click="showRenameDialog(file)" class="text-yellow-500">重命名</button>
                                    <button @click="confirmDelete(file)" class="text-red-500">删除</button>
                                    <div class="inline-block relative move-dropdown-container">
                                        <button @click="openMoveDropdown(file)" class="text-blue-500">移动</button>
                                        <div v-if="moveDropdownFile && moveDropdownFile.id === file.id" class="absolute z-10 bg-white border rounded shadow mt-1 w-40">
                                            <div @click="moveFileToFolder(file, null)" class="px-3 py-2 hover:bg-blue-100 cursor-pointer border-b">
                                                默认文件夹
                                            </div>
                                            <div v-for="folder in getFoldersInFolder(null)" :key="folder.id" @click="moveFileToFolder(file, folder.realFolderId)" class="px-3 py-2 hover:bg-blue-100 cursor-pointer">
                                                {{ folder.name }}
                                            </div>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                            <tr v-if="pagedFiles.length === 0">
                                <td colspan="6" class="text-center py-4 text-gray-400">暂无文件</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- 网格视图 -->
                <div v-else-if="viewMode==='grid'" class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div v-for="file in pagedFiles" :key="file.id" class="bg-white rounded shadow p-4 relative flex flex-col">
                        <div class="flex items-center mb-2">
                            <input type="checkbox" v-model="selectedFiles" :value="file.id" class="mr-2" />
                            <span class="font-bold text-blue-700">{{ file.name }}</span>
                        </div>
                        <div class="text-xs text-gray-500 mb-1">类型：{{ file.type }}</div>
                        <div class="text-xs text-gray-500 mb-1">上传者：{{ file.uploader }}</div>
                        <div class="text-xs text-gray-500 mb-1">上传时间：{{ file.uploadedAt }}</div>
                        <div class="flex items-center mt-2 space-x-2">
                            <button @click="downloadFileData(file)" class="text-blue-500 text-sm">下载</button>
                            <button @click="showRenameDialog(file)" class="text-yellow-500 text-sm">重命名</button>
                            <button @click="confirmDelete(file)" class="text-red-500 text-sm">删除</button>
                            <button @click="decompressFileData(file.id)" class="text-yellow-500 text-sm">解压</button>
                        </div>
                    </div>
                </div>

                <!-- 分页 -->
                <div class="flex justify-between items-center mt-4 text-sm">
                    <div>共 {{ filteredFiles.length }} 条</div>
                    <div class="space-x-2">
                        <button class="px-2" :disabled="page===1" @click="page--">上一页</button>
                        <span>{{ page }}</span>
                        <button class="px-2" :disabled="page===maxPage" @click="page++">下一页</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 弹窗部分保持不变 -->
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
                <div class="text-lg mb-6">确定要删除{{ deleteTarget?.isFolder ? '文件夹' : '文件' }} <span class="font-bold text-red-600">{{ deleteTarget?.name }}</span> 吗？</div>
                <div class="flex justify-end gap-4">
                    <button class="px-6 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" @click="showDeleteConfirm=false">取消</button>
                    <button class="px-6 py-2 rounded bg-red-600 text-white hover:bg-red-700" @click="deleteFileConfirm">删除</button>
                </div>
            </div>
        </div>

        <!-- 在线解压弹窗 -->
        <div v-if="decompressDialog" class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
            <div class="bg-white p-6 rounded shadow-lg w-96">
                <h3 class="text-lg font-bold mb-2">在线解压</h3>
                <div class="mb-2">将对所选文件进行在线解压，支持zip/rar/tar等格式。</div>
                <button @click="batchDecompressData" class="bg-yellow-500 text-white px-4 py-1 rounded mr-2">确定</button>
                <button @click="decompressDialog=false" class="bg-gray-300 px-4 py-1 rounded">取消</button>
            </div>
        </div>

        <!-- 重命名弹窗 -->
        <div v-if="renameDialog" class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
            <div class="bg-white p-6 rounded shadow-lg w-96">
                <h3 class="text-lg font-bold mb-2">重命名{{ renameFileObj?.isFolder ? '文件夹' : '文件' }}</h3>
                <input v-model="renameTarget" placeholder="新名称" class="border w-full mb-2 px-2 py-1" />
                <button @click="confirmRename" class="bg-yellow-500 text-white px-4 py-1 rounded mr-2">确定</button>
                <button @click="renameDialog=false" class="bg-gray-300 px-4 py-1 rounded">取消</button>
            </div>
        </div>

        <!-- 创建文件夹弹窗 -->
        <div v-if="showCreateFolderDialog" class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
            <div class="bg-white p-6 rounded shadow-lg w-96">
                <h3 class="text-lg font-bold mb-2">创建文件夹</h3>
                <div class="mb-4">
                    <label class="block text-gray-600 mb-1">文件夹名称</label>
                    <input v-model="newFolderName" placeholder="请输入文件夹名称" class="border w-full px-2 py-1" />
                </div>
                <div class="mb-4">
                    <label class="block text-gray-600 mb-1">描述（可选）</label>
                    <textarea v-model="newFolderDescription" placeholder="请输入文件夹描述" class="border w-full px-2 py-1 h-20"></textarea>
                </div>
                <div class="flex justify-end space-x-2">
                    <button @click="createFolder" class="bg-purple-500 text-white px-4 py-1 rounded">创建</button>
                    <button @click="showCreateFolderDialog=false" class="bg-gray-300 px-4 py-1 rounded">取消</button>
                </div>
            </div>
        </div>

        <!-- 上传进度 -->
        <div v-if="uploadProgress.length" class="mt-4">
            <h3 class="font-bold mb-2">上传进度</h3>
            <div v-for="item in uploadProgress" :key="item.name" class="mb-1">
                <span>{{ item.name }}：</span>
                <span>{{ item.percent }}%</span>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { fetchFiles, uploadFile, deleteFile, downloadFile, uploadChunk, batchDelete, batchDeleteMixed, batchDownload, batchDownloadMixed, decompressFile, batchDecompress, renameFile as renameFileAPI, createFolder as createFolderAPI, fetchFolders, deleteFolder as deleteFolderAPI, renameFolder as renameFolderAPI, moveFile } from '@/api.js'

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
const selectedFiles = ref([])
const allSelected = ref(false)
const decompressDialog = ref(false)
const uploadProgress = ref([])
const viewMode = ref('table')
const renameDialog = ref(false)
const renameTarget = ref('')
const renameFileObj = ref(null)
const showCreateFolderDialog = ref(false)
const newFolderName = ref('')
const newFolderDescription = ref('')
const expandedFolders = ref({ default: true })
const moveDropdownFile = ref(null)

// 获取文件列表
async function fetchFilesData() {
    try {
        // 获取文件列表
        const filesRes = await fetchFiles()
        const files = (filesRes.data.files || []).map(file => ({
            id: file.id,
            name: file.original_filename,
            size: formatFileSize(file.file_size),
            type: file.file_type,
            time: file.created_at,
            uploader: file.uploader_name,
            uploadedAt: file.created_at,
            isFolder: false,
            description: file.description,
            tags: file.tags,
            folderId: file.folder_id
        }))
        
        // 获取文件夹列表
        const foldersRes = await fetchFolders()
        const folders = (foldersRes.data.folders || []).map(folder => ({
            id: `folder_${folder.id}`,
            name: folder.name,
            size: '-',
            type: '文件夹',
            time: folder.created_at,
            uploader: folder.uploader_name,
            uploadedAt: folder.created_at,
            isFolder: true,
            description: folder.description,
            folderId: folder.id,
            realFolderId: folder.id
        }))
        
        // 合并文件和文件夹，确保文件夹在前面显示
        allFiles.value = [...folders, ...files]
    } catch (e) {
        console.error('获取文件列表失败:', e)
        allFiles.value = []
    }
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(() => {
    fetchFilesData()
    
    // 添加全局点击事件监听，点击空白处关闭下拉菜单
    document.addEventListener('click', handleGlobalClick)
})

// 在组件卸载时移除事件监听
onUnmounted(() => {
    document.removeEventListener('click', handleGlobalClick)
})

function handleGlobalClick(event) {
    // 如果点击的不是移动下拉菜单相关元素，则关闭下拉菜单
    if (!event.target.closest('.move-dropdown-container')) {
        moveDropdownFile.value = null
    }
}

const filteredFiles = computed(() => {
    let files = allFiles.value.filter(f => {
        const nameMatch = !searchName.value || f.name.includes(searchName.value)
        const uploaderMatch = !searchUploader.value || f.uploader.includes(searchUploader.value)
        const dateMatch = !searchDate.value || f.time.startsWith(searchDate.value)
        
        return nameMatch && uploaderMatch && dateMatch
    })
    
    // 在表格和网格视图中，只显示文件，不显示文件夹
    if (viewMode.value === 'table' || viewMode.value === 'grid') {
        files = files.filter(f => !f.isFolder)
    }
    
    return files
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
            const response = await uploadFile(formData)
            console.log('上传成功:', response)
            await fetchFilesData()
            alert('上传成功')
        } catch (err) {
            console.error('上传失败:', err)
            if (err.response && err.response.data && err.response.data.detail) {
                alert('上传失败: ' + err.response.data.detail)
            } else if (err.message) {
                alert('上传失败: ' + err.message)
            } else {
                alert('上传失败，请检查网络连接')
            }
        }
    }
}
// 删除文件
async function deleteFileConfirm() {
    if (!deleteTarget.value) return
    try {
        if (deleteTarget.value.isFolder) {
            // 删除文件夹
            await deleteFolderAPI(deleteTarget.value.folderId)
        } else {
            // 删除文件
            await deleteFile(deleteTarget.value.id)
        }
        await fetchFilesData()
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
async function downloadFileData(file) {
    try {
        const res = await downloadFile(file.id)
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
function toggleAll(e) {
    allSelected.value = e.target.checked
    selectedFiles.value = allSelected.value ? filteredFiles.value.map(f => f.id) : []
}
async function batchDeleteData() {
    try {
        // 分离文件和文件夹ID
        const fileIds = []
        const folderIds = []
        
        for (const selectedId of selectedFiles.value) {
            if (selectedId.startsWith('folder_')) {
                // 这是文件夹选择，只在树形视图中处理
                if (viewMode.value === 'tree') {
                    const folderId = selectedId.replace('folder_', '')
                    if (folderId === 'default') {
                        // 默认文件夹下的文件
                        const defaultFiles = getFilesInFolder(null)
                        fileIds.push(...defaultFiles.map(f => f.id))
                    } else {
                        // 具体文件夹
                        folderIds.push(parseInt(folderId))
                    }
                }
            } else {
                // 这是文件选择
                fileIds.push(parseInt(selectedId))
            }
        }
        
        if (fileIds.length === 0 && folderIds.length === 0) {
            alert('请选择要删除的文件或文件夹')
            return
        }
        
        // 调用混合批量删除API
        const result = await batchDeleteMixed(fileIds, folderIds)
        
        // 显示删除结果
        const message = `批量删除完成！\n删除文件：${result.data.deleted_files} 个\n删除文件夹：${result.data.deleted_folders} 个`
        alert(message)
        
        selectedFiles.value = []
        await fetchFilesData()
    } catch (err) {
        console.error('批量删除失败:', err)
        if (err.response && err.response.data && err.response.data.detail) {
            alert('批量删除失败: ' + err.response.data.detail)
        } else {
            alert('批量删除失败')
        }
    }
}
async function batchDownloadData() {
    try {
        // 分离文件和文件夹ID
        const fileIds = []
        const folderIds = []
        
        for (const selectedId of selectedFiles.value) {
            if (selectedId.startsWith('folder_')) {
                // 这是文件夹选择，只在树形视图中处理
                if (viewMode.value === 'tree') {
                    const folderId = selectedId.replace('folder_', '')
                    if (folderId === 'default') {
                        // 默认文件夹下的文件
                        const defaultFiles = getFilesInFolder(null)
                        fileIds.push(...defaultFiles.map(f => f.id))
                    } else {
                        // 具体文件夹
                        folderIds.push(parseInt(folderId))
                    }
                }
            } else {
                // 这是文件选择
                fileIds.push(parseInt(selectedId))
            }
        }
        
        if (fileIds.length === 0 && folderIds.length === 0) {
            alert('请选择要下载的文件或文件夹')
            return
        }
        
        // 调用混合批量下载API
        const res = await batchDownloadMixed(fileIds, folderIds)
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([res.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', '批量下载.zip')
        document.body.appendChild(link)
        link.click()
        link.remove()
        
        // 清理选择
        selectedFiles.value = []
    } catch (err) {
        console.error('批量下载失败:', err)
        if (err.response && err.response.data && err.response.data.detail) {
            alert('批量下载失败: ' + err.response.data.detail)
        } else {
            alert('批量下载失败')
        }
    }
}
async function decompressFileData(id) {
    try {
        const res = await decompressFile(id)
        alert('解压成功！解压目录：' + res.data.extract_dir)
        await fetchFilesData()
    } catch (err) {
        console.error('解压失败:', err)
        if (err.response && err.response.data && err.response.data.detail) {
            alert('解压失败: ' + err.response.data.detail)
        } else {
            alert('解压失败')
        }
    }
}
async function batchDecompressData() {
    if (selectedFiles.value.length === 0) {
        alert('请选择要解压的文件')
        return
    }
    
    try {
        const res = await batchDecompress(selectedFiles.value)
        const results = res.data.results
        const successCount = results.filter(r => r.status === 'success').length
        const errorCount = results.filter(r => r.status === 'error').length
        
        let message = `批量解压完成！\n成功：${successCount} 个文件\n失败：${errorCount} 个文件`
        
        if (errorCount > 0) {
            message += '\n\n失败的文件：'
            results.filter(r => r.status === 'error').forEach(r => {
                message += `\n- ${r.filename}: ${r.message}`
            })
        }
        
        alert(message)
        decompressDialog.value = false
        selectedFiles.value = []
        await fetchFilesData()
    } catch (err) {
        console.error('批量解压失败:', err)
        if (err.response && err.response.data && err.response.data.detail) {
            alert('批量解压失败: ' + err.response.data.detail)
        } else {
            alert('批量解压失败')
        }
    }
}
async function uploadFiles() {
    // 断点续传（分片上传）示例，实际需后端配合
    uploadProgress.value = []
    for (const file of fileList.value) {
        let uploaded = 0
        const chunkSize = 1024 * 1024 * 2 // 2MB
        const total = file.size
        let chunkIndex = 0
        while (uploaded < total) {
            const chunk = file.slice(uploaded, uploaded + chunkSize)
            const formData = new FormData()
            formData.append('file', chunk)
            formData.append('name', file.name)
            formData.append('chunkIndex', chunkIndex)
            formData.append('totalChunks', Math.ceil(total / chunkSize))
            await uploadChunk(formData)
            uploaded += chunk.size
            chunkIndex++
            updateProgress(file.name, Math.min(100, Math.round((uploaded / total) * 100)))
        }
    }
    fileList.value = []
    await fetchFilesData()
}
function updateProgress(name, percent) {
    const idx = uploadProgress.value.findIndex(i => i.name === name)
    if (idx >= 0) uploadProgress.value[idx].percent = percent
    else uploadProgress.value.push({ name, percent })
}
function enterFolder(file) {
    // 实现进入文件夹的逻辑
    console.log('Entering folder:', file.name)
}
function showRenameDialog(file) {
    renameFileObj.value = file
    renameTarget.value = file.name
    renameDialog.value = true
}
async function confirmRename() {
    if (!renameFileObj.value || !renameTarget.value.trim()) {
        alert('请输入新名称')
        return
    }
    
    try {
        if (renameFileObj.value.isFolder) {
            // 重命名文件夹
            await renameFolderAPI(renameFileObj.value.folderId, renameTarget.value.trim())
        } else {
            // 重命名文件
            await renameFileAPI(renameFileObj.value.id, renameTarget.value.trim())
        }
        alert('重命名成功')
        renameDialog.value = false
        renameFileObj.value = null
        renameTarget.value = ''
        await fetchFilesData()
    } catch (err) {
        console.error('重命名失败:', err)
        if (err.response && err.response.data && err.response.data.detail) {
            alert('重命名失败: ' + err.response.data.detail)
        } else {
            alert('重命名失败')
        }
    }
}
async function createFolder() {
    if (!newFolderName.value.trim()) {
        alert('请输入文件夹名称')
        return
    }
    
    try {
        // 创建文件夹时，parent_id为null，表示都是兄弟关系
        await createFolderAPI(newFolderName.value.trim(), null, newFolderDescription.value.trim())
        alert('文件夹创建成功')
        showCreateFolderDialog.value = false
        newFolderName.value = ''
        newFolderDescription.value = ''
        await fetchFilesData()
    } catch (err) {
        console.error('创建文件夹失败:', err)
        if (err.response && err.response.data && err.response.data.detail) {
            alert('创建文件夹失败: ' + err.response.data.detail)
        } else {
            alert('创建文件夹失败')
        }
    }
}
function toggleFolder(folderId) {
    expandedFolders.value[folderId] = !expandedFolders.value[folderId]
}
function getFilesInFolder(folderId) {
    // 默认文件夹（folderId为null）
    if (folderId === null || folderId === 'default') {
        return allFiles.value.filter(f => !f.isFolder && (f.folderId === null || f.folderId === undefined))
    }
    // 其他文件夹
    return allFiles.value.filter(f => !f.isFolder && f.folderId === folderId)
}
function getFoldersInFolder(folderId) {
    if (folderId === null) {
        // 根目录下的文件夹，都是兄弟关系
        return allFiles.value.filter(f => f.isFolder)
    }
    return allFiles.value.filter(f => f.isFolder && f.folderId === folderId)
}
function openMoveDropdown(file) {
    if (moveDropdownFile.value && moveDropdownFile.value.id === file.id) {
        moveDropdownFile.value = null
    } else {
        moveDropdownFile.value = file
    }
}
async function moveFileToFolder(file, folderId) {
    console.log('开始移动文件:', { fileId: file.id, fileName: file.name, folderId: folderId })
    try {
        console.log('调用moveFile API...')
        const response = await moveFile(file.id, folderId)
        console.log('moveFile API响应:', response)
        
        moveDropdownFile.value = null
        
        // 立即更新本地数据，确保UI立即响应
        const fileIndex = allFiles.value.findIndex(f => f.id === file.id)
        if (fileIndex !== -1) {
            allFiles.value[fileIndex].folderId = folderId
            console.log('本地数据已更新')
        }
        
        // 刷新数据以确保与服务器同步
        console.log('刷新文件列表...')
        await fetchFilesData()
        
        // 修复文件夹名称查找逻辑
        let targetFolderName = '默认文件夹'
        if (folderId !== null) {
            const folder = allFiles.value.find(f => f.isFolder && f.realFolderId === folderId)
            targetFolderName = folder ? folder.name : '未知文件夹'
        }
        
        console.log('移动成功，目标文件夹:', targetFolderName)
        alert(`文件 "${file.name}" 已成功移动到 ${targetFolderName}`)
    } catch (err) {
        console.error('移动文件失败，详细错误:', err)
        console.error('错误响应:', err.response)
        console.error('错误状态:', err.response?.status)
        console.error('错误数据:', err.response?.data)
        
        if (err.response && err.response.data && err.response.data.detail) {
            alert('移动失败: ' + err.response.data.detail)
        } else {
            alert('移动失败，请检查网络连接')
        }
    }
}
</script>