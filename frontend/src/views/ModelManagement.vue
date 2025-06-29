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
                                    <button class="text-green-500 hover:underline" @click="downloadModelData(model)">下载</button>
                                    <button class="text-indigo-500 hover:underline" @click="exportOnnx(model)">导出onnx</button>
                                    <button class="text-blue-600 hover:underline" @click="openEvalDialog(model)">测试</button>
                                    <button class="text-blue-600 hover:underline" @click="openPredictDialog(model)">预测</button>
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
                <!-- 评估任务弹窗 -->
                <div v-if="evalDialogVisible" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-30 z-50">
                    <div class="bg-white rounded-xl shadow-xl p-8 w-full max-w-lg relative">
                        <button class="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl" @click="evalDialogVisible=false">×</button>
                        <h2 class="text-2xl font-bold mb-6 text-center">新建模型评估任务</h2>
                        <form @submit.prevent="submitEvalTask">
                            <div class="mb-4">
                                <label class="block text-gray-600 mb-1">任务名称</label>
                                <input v-model="evalForm.name" type="text" class="w-full px-3 py-2 border rounded" required />
                            </div>
                            <div class="mb-4">
                                <label class="block text-gray-600 mb-1">评估参数</label>
                                <textarea v-model="evalForm.params" class="w-full px-3 py-2 border rounded" rows="3" placeholder="如 batch_size=32, attack=fgsm"></textarea>
                            </div>
                            <div class="mb-4">
                                <label class="block text-gray-600 mb-1">资源分配</label>
                                <select v-model="evalForm.resource" class="w-full px-3 py-2 border rounded">
                                    <option value="CPU">CPU</option>
                                    <option value="GPU">GPU</option>
                                </select>
                            </div>
                            <div class="flex justify-end gap-4">
                                <button type="button" class="px-6 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" @click="evalDialogVisible=false">取消</button>
                                <button type="submit" class="px-6 py-2 rounded bg-blue-600 text-white hover:bg-blue-700">立即创建</button>
                            </div>
                        </form>
                    </div>
                </div>
                <!-- 预测任务弹窗 -->
                <div v-if="predictDialogVisible" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-30 z-50">
                    <div class="bg-white rounded-xl shadow-xl p-8 w-full max-w-lg relative">
                        <button class="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl" @click="predictDialogVisible=false">×</button>
                        <h2 class="text-2xl font-bold mb-6 text-center">新建模型预测任务</h2>
                        <form @submit.prevent="submitPredictTask">
                            <div class="mb-4">
                                <label class="block text-gray-600 mb-1">任务名称</label>
                                <input v-model="predictForm.name" type="text" class="w-full px-3 py-2 border rounded" required />
                            </div>
                            <div class="mb-4">
                                <label class="block text-gray-600 mb-1">预测参数</label>
                                <textarea v-model="predictForm.params" class="w-full px-3 py-2 border rounded" rows="3" placeholder="如 batch_size=32, input_path=xxx"></textarea>
                            </div>
                            <div class="mb-4">
                                <label class="block text-gray-600 mb-1">资源分配</label>
                                <select v-model="predictForm.resource" class="w-full px-3 py-2 border rounded">
                                    <option value="CPU">CPU</option>
                                    <option value="GPU">GPU</option>
                                </select>
                            </div>
                            <div class="flex justify-end gap-4">
                                <button type="button" class="px-6 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" @click="predictDialogVisible=false">取消</button>
                                <button type="submit" class="px-6 py-2 rounded bg-blue-600 text-white hover:bg-blue-700">立即创建</button>
                            </div>
                        </form>
                    </div>
                </div>
                <!-- 任务中心弹窗 -->
                <div v-if="taskCenterVisible" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-30 z-50">
                    <div class="bg-white rounded-xl shadow-xl p-8 w-full max-w-5xl relative">
                        <button class="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl" @click="taskCenterVisible=false">×</button>
                        <h2 class="text-2xl font-bold mb-6 text-center">模型预测与评估任务中心</h2>
                        <div class="flex">
                            <div class="w-2/3 pr-6 border-r">
                                <table class="min-w-full text-sm">
                                    <thead class="bg-gray-100">
                                        <tr>
                                            <th class="py-2 px-4 border-b">任务ID</th>
                                            <th class="py-2 px-4 border-b">类型</th>
                                            <th class="py-2 px-4 border-b">模型</th>
                                            <th class="py-2 px-4 border-b">状态</th>
                                            <th class="py-2 px-4 border-b">进度</th>
                                            <th class="py-2 px-4 border-b">创建时间</th>
                                            <th class="py-2 px-4 border-b">操作</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="task in taskList" :key="task.id" :class="{'bg-blue-50': task.id===selectedTask?.id}" @click="selectTask(task)">
                                            <td class="py-2 px-4 border-b">{{ task.id }}</td>
                                            <td class="py-2 px-4 border-b">{{ task.type }}</td>
                                            <td class="py-2 px-4 border-b">{{ task.modelName }}</td>
                                            <td class="py-2 px-4 border-b">{{ task.status }}</td>
                                            <td class="py-2 px-4 border-b">{{ task.progress }}</td>
                                            <td class="py-2 px-4 border-b">{{ task.createdAt }}</td>
                                            <td class="py-2 px-4 border-b space-x-2">
                                                <button class="text-blue-500 hover:underline" @click.stop="selectTask(task)">回显</button>
                                                <button class="text-red-500 hover:underline" @click.stop="deleteTask(task)">删除</button>
                                            </td>
                                        </tr>
                                        <tr v-if="taskList.length===0">
                                            <td colspan="7" class="text-center py-4 text-gray-400">暂无任务</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                            <div class="w-1/3 pl-6">
                                <div v-if="selectedTask">
                                    <div class="mb-2 flex space-x-2">
                                        <button :class="['px-3 py-1 rounded', taskTab==='params'?'bg-blue-500 text-white':'bg-gray-100']" @click="taskTab='params'">预测/评估参数</button>
                                        <button :class="['px-3 py-1 rounded', taskTab==='log'?'bg-blue-500 text-white':'bg-gray-100']" @click="taskTab='log'">日志</button>
                                        <button :class="['px-3 py-1 rounded', taskTab==='result'?'bg-blue-500 text-white':'bg-gray-100']" @click="taskTab='result'">结果</button>
                                    </div>
                                    <div v-if="taskTab==='params'">
                                        <table class="w-full text-sm mb-2">
                                            <tr v-for="(v,k) in selectedTask.paramsObj" :key="k"><td class="text-gray-500 w-1/3">{{k}}</td><td>{{v}}</td></tr>
                                        </table>
                                    </div>
                                    <div v-if="taskTab==='log'">
                                        <textarea class="w-full h-40 border rounded p-2" readonly :value="selectedTask.log"></textarea>
                                    </div>
                                    <div v-if="taskTab==='result'">
                                        <div v-if="selectedTask.resultImg">
                                            <img :src="selectedTask.resultImg" alt="结果可视化" class="max-w-full max-h-40 mb-2" />
                                        </div>
                                        <div v-if="selectedTask.resultText" class="bg-gray-50 p-2 rounded text-sm">{{selectedTask.resultText}}</div>
                                        <div v-if="!selectedTask.resultImg && !selectedTask.resultText" class="text-gray-400">暂无结果</div>
                                    </div>
                                </div>
                                <div v-else class="text-gray-400 mt-12 text-center">请选择左侧任务查看详情</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchModels, uploadModel, deleteModel, downloadModel, exportModelOnnx, createModelEvalTask, createModelPredictTask, getModelTaskList, getModelTaskDetail } from '@/api.js'

const allModels = ref([])
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
const fileInput = ref(null)
const evalDialogVisible = ref(false)
const predictDialogVisible = ref(false)
const evalForm = ref({ name: '', params: '', resource: 'CPU' })
const predictForm = ref({ name: '', params: '', resource: 'CPU' })
const taskCenterVisible = ref(false)
const taskList = ref([])
const selectedTask = ref(null)
const taskTab = ref('params')
let currentModel = null
let progressTimers = {}

async function fetchModelsData() {
    try {
        const res = await fetchModels()
        allModels.value = res.data.models || []
    } catch (e) {
        allModels.value = []
    }
}

onMounted(() => {
    fetchModelsData()
})

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
// 上传模型
async function handleFileChange(e) {
    const fileList = e.target.files
    if (fileList.length > 0) {
        const file = fileList[0]
        const formData = new FormData()
        formData.append('file', file)
        try {
            await uploadModel(formData)
            await fetchModelsData()
            alert('上传成功')
        } catch (err) {
            alert('上传失败')
        }
    }
}
// 删除模型
async function deleteModelConfirm() {
    if (!deleteTarget.value) return
    try {
        await deleteModel(deleteTarget.value.id)
        await fetchModelsData()
        showDeleteConfirm.value = false
        deleteTarget.value = null
    } catch (err) {
        alert('删除失败')
    }
}
function confirmDelete(model) {
    deleteTarget.value = model
    showDeleteConfirm.value = true
}
function addModel() {
    fileInput.value.click()
}
function editModel(model) {
    form.value = { ...model }
    showEditForm.value = true
}
function updateModel() {
    // 可扩展：实现模型信息编辑接口
    closeForm()
}
function showDetail(model) {
    alert('模型详情：' + model.name)
}
function openEvalDialog(model) {
    currentModel = model
    evalForm.value = { name: model.name + '-评估', params: '', resource: 'CPU' }
    evalDialogVisible.value = true
}
function openPredictDialog(model) {
    currentModel = model
    predictForm.value = { name: model.name + '-预测', params: '', resource: 'CPU' }
    predictDialogVisible.value = true
}
function openTaskCenter() {
    taskCenterVisible.value = true
    if (taskList.value.length>0) selectTask(taskList.value[0])
}
function selectTask(task) {
    selectedTask.value = task
    taskTab.value = 'params'
}
function deleteTask(task) {
    taskList.value = taskList.value.filter(t=>t.id!==task.id)
    if(selectedTask.value?.id===task.id) selectedTask.value=null
}
function submitEvalTask() {
    evalDialogVisible.value = false
    const id = Date.now()+''+Math.floor(Math.random()*1000)
    const task = {
        id,
        type: '评估',
        modelName: currentModel?.name,
        status: '运行中',
        progress: '0%',
        createdAt: new Date().toLocaleString(),
        paramsObj: Object.fromEntries(evalForm.value.params.split(',').map(s=>s.split('=')).filter(a=>a.length===2)),
        log: '',
        resultImg: '',
        resultText: ''
    }
    taskList.value.unshift(task)
    simulateTaskProgress(task)
    openTaskCenter()
}
function submitPredictTask() {
    predictDialogVisible.value = false
    const id = Date.now()+''+Math.floor(Math.random()*1000)
    const task = {
        id,
        type: '预测',
        modelName: currentModel?.name,
        status: '运行中',
        progress: '0%',
        createdAt: new Date().toLocaleString(),
        paramsObj: Object.fromEntries(predictForm.value.params.split(',').map(s=>s.split('=')).filter(a=>a.length===2)),
        log: '',
        resultImg: '',
        resultText: ''
    }
    taskList.value.unshift(task)
    simulateTaskProgress(task)
    openTaskCenter()
}
function simulateTaskProgress(task) {
    let percent = 0
    if(progressTimers[task.id]) clearInterval(progressTimers[task.id])
    progressTimers[task.id] = setInterval(()=>{
        if(percent<100) {
            percent += Math.floor(Math.random()*20+10)
            if(percent>100) percent=100
            task.progress = percent+'%'
        }
        if(percent>=100) {
            task.status = '成功'
            task.log = '任务已完成，日志内容...';
            task.resultText = task.type==='评估' ? '评估指标：准确率0.92，鲁棒性0.85' : '预测结果：类别A，置信度0.88';
            if(task.type==='预测') task.resultImg = 'https://via.placeholder.com/120x40?text=Result';
            clearInterval(progressTimers[task.id])
        }
    }, 800)
}
// 下载模型
async function downloadModelData(model) {
    try {
        const res = await downloadModel(model.id)
        const url = window.URL.createObjectURL(new Blob([res.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', model.name)
        document.body.appendChild(link)
        link.click()
        link.remove()
    } catch (err) {
        alert('下载失败')
    }
}
// 导出ONNX
async function exportOnnx(model) {
    try {
        const res = await exportModelOnnx(model.id)
        const url = window.URL.createObjectURL(new Blob([res.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${model.name}.onnx`)
        document.body.appendChild(link)
        link.click()
        link.remove()
    } catch (err) {
        alert('导出失败')
    }
}
// 新建评估任务
async function createEvalTask(model) {
    try {
        const taskData = {
            model_id: model.id,
            name: `${model.name}_评估任务`,
            params: {},
            resource: {}
        }
        await createModelEvalTask(taskData)
        alert('评估任务创建成功')
    } catch (err) {
        alert('评估任务创建失败')
    }
}
// 新建预测任务
async function createPredictTask(model) {
    try {
        const taskData = {
            model_id: model.id,
            name: `${model.name}_预测任务`,
            params: {},
            resource: {}
        }
        await createModelPredictTask(taskData)
        alert('预测任务创建成功')
    } catch (err) {
        alert('预测任务创建失败')
    }
}
// 获取任务列表
async function getTaskList(modelId) {
    try {
        const res = await getModelTaskList({ model_id: modelId })
        return res.data.tasks || []
    } catch (err) {
        return []
    }
}
// 获取任务详情
async function getTaskDetail(taskId) {
    try {
        const res = await getModelTaskDetail(taskId)
        return res.data
    } catch (err) {
        return null
    }
}
</script>