<template>
  <div class="p-8 bg-gray-50 min-h-screen">
    <div class="max-w-7xl mx-auto">
      <div class="bg-white rounded-xl shadow p-8">
        <div class="flex items-center mb-6 justify-between">
          <div class="flex space-x-2">
            <input v-model="searchName" type="text" placeholder="请输入算法名称" class="border rounded px-3 py-2 focus:outline-none focus:ring w-48" />
            <select v-model="searchType" class="border rounded px-3 py-2 w-32">
              <option value="">全部类型</option>
              <option v-for="t in typeList" :key="t" :value="t">{{ t }}</option>
            </select>
            <button @click="filterAlgorithms" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">查询</button>
            <button @click="resetFilters" class="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300">重置</button>
          </div>
          <div class="flex space-x-2">
            <button @click="addAlgorithm()" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">+ 新建算法</button>
            <button @click="subscribeDialog=true" class="bg-blue-400 text-white px-4 py-2 rounded hover:bg-blue-500">订阅列表</button>
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="algo in pagedAlgorithms" :key="algo.id" class="bg-gray-50 rounded-xl shadow p-6 relative group">
            <div class="flex items-center mb-2">
              <span class="text-xs bg-gray-200 rounded px-2 py-1 mr-2" v-if="algo.type">{{ algo.type }}</span>
              <span class="font-bold text-lg">{{ algo.name }}</span>
              <span class="ml-2 text-xs text-gray-400">V{{ algo.version }}</span>
            </div>
            <div class="text-gray-500 text-sm mb-2">{{ algo.description }}</div>
            <div class="flex flex-wrap gap-2 mb-2">
              <span v-if="algo.trainable" class="text-green-600 text-xs bg-green-100 rounded px-2 py-0.5">训练</span>
              <span v-if="algo.evaluable" class="text-blue-600 text-xs bg-blue-100 rounded px-2 py-0.5">模型评估</span>
              <span v-if="algo.inferable" class="text-yellow-600 text-xs bg-yellow-100 rounded px-2 py-0.5">推理服务</span>
            </div>
            <div class="flex items-center text-xs text-gray-400 mb-2">
              <span>上传人：{{ algo.uploader }}</span>
              <span class="ml-4">{{ algo.uploadedAt }}</span>
            </div>
            <div class="flex items-center space-x-2 mt-2">
              <el-button size="mini" @click="goToDetail(algo)">详情</el-button>
              <button class="text-yellow-500 hover:underline" @click="editAlgorithm(algo)">编辑</button>
              <button class="text-purple-500 hover:underline" @click="cloneAlgorithm(algo)">克隆</button>
              <button class="text-cyan-500 hover:underline" @click="subscribeAlgorithm(algo)">订阅</button>
              <button class="text-red-500 hover:underline" @click="confirmDelete(algo)">删除</button>
            </div>
            <div class="absolute top-2 right-2 flex space-x-1 opacity-0 group-hover:opacity-100 transition">
              <button class="text-gray-400 hover:text-gray-700" @click="copyAlgorithm(algo)"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16h8M8 12h8m-7 8h6a2 2 0 002-2V6a2 2 0 00-2-2H8a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg></button>
            </div>
          </div>
        </div>
        <div class="flex justify-between items-center mt-8 text-sm">
          <div>共 {{ filteredAlgorithms.length }} 条</div>
          <div class="space-x-2">
            <button class="px-2" :disabled="page===1" @click="page--">上一页</button>
            <span>{{ page }}</span>
            <button class="px-2" :disabled="page===maxPage" @click="page++">下一页</button>
          </div>
        </div>
        <!-- 新建/编辑算法弹窗 -->
        <el-dialog :visible.sync="dialogVisible" width="600px" :title="isEdit ? '编辑算法' : '新建算法'" @close="resetForm">
          <el-steps :active="step" finish-status="success" align-center class="mb-6">
            <el-step title="基本信息" />
            <el-step title="上传/导入" />
            <el-step title="目录结构" />
            <el-step title="配置文件" />
          </el-steps>
          <div v-show="step === 0">
            <el-form :model="form" label-width="90px">
              <el-form-item label="算法名称" required>
                <el-input v-model="form.name" placeholder="请输入算法名称" />
              </el-form-item>
              <el-form-item label="描述">
                <el-input v-model="form.desc" type="textarea" placeholder="请输入描述" />
              </el-form-item>
              <el-form-item label="类型">
                <el-select v-model="form.type" placeholder="请选择类型">
                  <el-option v-for="t in typeList" :key="t" :label="t" :value="t" />
                </el-select>
              </el-form-item>
              <el-form-item label="应用网络">
                <el-input v-model="form.network" placeholder="如ResNet、BERT等" />
              </el-form-item>
              <el-form-item label="版本">
                <el-input v-model="form.version" placeholder="如v1.0" />
              </el-form-item>
            </el-form>
          </div>
          <div v-show="step === 1">
            <el-upload drag multiple :auto-upload="false" :file-list="form.files" @change="handleFileChange">
              <i class="el-icon-upload"></i>
              <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            </el-upload>
          </div>
          <div v-show="step === 2">
            <div class="bg-gray-100 p-4 rounded mb-2">（此处可展示/编辑算法目录结构，支持上传/新建/删除文件夹和文件，后续可扩展为树形结构）</div>
            <el-input v-model="form.structure" type="textarea" rows="4" placeholder="可选：填写或粘贴目录结构描述" />
          </div>
          <div v-show="step === 3">
            <el-input v-model="form.config" type="textarea" rows="8" placeholder="可选：填写或粘贴config.yml内容" />
          </div>
          <div class="flex justify-between mt-6">
            <el-button @click="prevStep" :disabled="step===0">上一步</el-button>
            <el-button v-if="step<3" type="primary" @click="nextStep">下一步</el-button>
            <el-button v-else type="success" @click="submitForm">提交</el-button>
          </div>
        </el-dialog>
        <!-- 删除确认弹窗 -->
        <div v-if="showDeleteConfirm" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-30 z-50">
          <div class="bg-white rounded-xl shadow-xl p-8 w-full max-w-sm relative">
            <div class="text-lg mb-6">确定要删除算法 <span class="font-bold text-red-600">{{ deleteTarget?.name }}</span> 吗？</div>
            <div class="flex justify-end gap-4">
              <button class="px-6 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" @click="showDeleteConfirm=false">取消</button>
              <button class="px-6 py-2 rounded bg-red-600 text-white hover:bg-red-700" @click="deleteAlgorithmConfirm">删除</button>
            </div>
          </div>
        </div>
        <!-- 订阅列表弹窗 -->
        <el-dialog :visible.sync="subscribeDialog" width="500px" title="我的订阅算法">
          <el-table :data="subscribedAlgorithms" style="width:100%">
            <el-table-column prop="name" label="算法名称" />
            <el-table-column prop="type" label="类型" width="100" />
            <el-table-column prop="version" label="版本" width="80" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="mini" @click="goToDetail(row)">详情</el-button>
                <el-button size="mini" type="danger" @click="unsubscribe(row)">取消订阅</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="mt-4 text-right">
            <el-button @click="subscribeDialog=false">关闭</el-button>
          </div>
        </el-dialog>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAlgorithmTree, fetchAlgorithms, uploadAlgorithmFile, createAlgorithmFolder, deleteAlgorithmFile, renameAlgorithmFile, uploadAlgorithm, deleteAlgorithm, getAlgorithmInfo, getDebugLogs, runDebug } from '@/api.js'
import { ElMessage, ElLoading } from 'element-plus'

const allAlgorithms = ref([])
const searchName = ref('')
const searchType = ref('')
const typeList = ref(['目标检测','语义分割','图像分类','机器学习','其他'])
const page = ref(1)
const pageSize = 9
const showAddForm = ref(false)
const showEditForm = ref(false)
const showDeleteConfirm = ref(false)
const showSubscribeList = ref(false)
const deleteTarget = ref(null)
const form = ref({ id: null, name: '', uploader: '', uploadedAt: '', status: '已部署' })
const fileInput = ref(null)
const dialogVisible = ref(false)
const isEdit = ref(false)
const step = ref(0)
const subscribeDialog = ref(false)
const subscribedAlgorithms = ref([
  // 示例数据，后续可用接口替换
  { id: 1, name: 'BERT文本分类', type: 'NLP', version: 'v1.0' },
  { id: 2, name: 'ResNet图像识别', type: 'CV', version: 'v2.1' }
])
const loading = ref(false)
const error = ref('')
const algorithms = ref([])
const treeData = ref([])

async function loadAlgorithms() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetchAlgorithms()
    algorithms.value = res.data.algorithms
  } catch (e) {
    error.value = '算法列表加载失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}
async function loadTree(id) {
  loading.value = true
  error.value = ''
  try {
    const res = await getAlgorithmTree(id)
    treeData.value = res.data.tree
  } catch (e) {
    error.value = '目录结构加载失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAlgorithms()
})

const filteredAlgorithms = computed(() => {
    return allAlgorithms.value.filter(a => {
        return (
            (!searchName.value || a.name.includes(searchName.value)) &&
            (!searchType.value || a.type === searchType.value)
        )
    })
})
const maxPage = computed(() => Math.max(1, Math.ceil(filteredAlgorithms.value.length / pageSize)))
const pagedAlgorithms = computed(() => {
    const start = (page.value - 1) * pageSize
    return filteredAlgorithms.value.slice(start, start + pageSize)
})
function filterAlgorithms() {
    page.value = 1
}
function resetFilters() {
    searchName.value = ''
    searchType.value = ''
    page.value = 1
}
function closeForm() {
    showAddForm.value = false
    showEditForm.value = false
    form.value = { id: null, name: '', uploader: '', uploadedAt: '', status: '已部署' }
}
// 上传算法
async function handleFileChange(file, fileList) {
    form.value.files = fileList
}
// 删除算法
async function deleteAlgorithmConfirm() {
    if (!deleteTarget.value) return
    try {
        await deleteAlgorithm(deleteTarget.value.id)
        await loadAlgorithms()
        showDeleteConfirm.value = false
        deleteTarget.value = null
        alert('算法删除成功')
    } catch (err) {
        alert('算法删除失败')
    }
}
function confirmDelete(algo) {
    deleteTarget.value = algo
    showDeleteConfirm.value = true
}
function addAlgorithm() {
    dialogVisible.value = true
    isEdit.value = false
    step.value = 0
    form.value = { id: null, name: '', uploader: '', uploadedAt: '', status: '已部署', files: [], desc: '', type: '', network: '', version: '', structure: '', config: '' }
}
function editAlgorithm(algo) {
    dialogVisible.value = true
    isEdit.value = true
    step.value = 0
    form.value = { ...algo }
}
function updateAlgorithm() {
    // 可扩展：实现算法信息编辑接口
    closeForm()
}
function showDetail(algo) {
    // TODO: 打开算法详情弹窗/页面
}
function cloneAlgorithm(algo) {
    // TODO: 克隆算法
}
function subscribeAlgorithm(algo) {
    // TODO: 订阅算法
}
function copyAlgorithm(algo) {
    // TODO: 复制算法信息
}
function nextStep() {
    if (step.value < 3) step.value++
}
function prevStep() {
    if (step.value > 0) step.value--
}
function resetForm() {
    step.value = 0
    form.value = { id: null, name: '', uploader: '', uploadedAt: '', status: '已部署', files: [], desc: '', type: '', network: '', version: '', structure: '', config: '' }
    isEdit.value = false
}
function submitForm() {
    // TODO: 提交表单逻辑，调用后端接口
    dialogVisible.value = false
    resetForm()
    alert('提交成功！')
}
function goToDetail(algo) {
    // TODO: 打开算法详情弹窗/页面
}
function unsubscribe(row) {
    // 取消订阅逻辑，后续可调用接口
    subscribedAlgorithms.value = subscribedAlgorithms.value.filter(a => a.id !== row.id)
    alert('已取消订阅：' + row.name)
}
// 获取算法详情
async function getAlgorithmDetail(id) {
    try {
        const res = await getAlgorithmInfo(id)
        return res.data
    } catch (err) {
        return null
    }
}

// 获取调试日志
async function getDebugLogsData(id) {
    try {
        const res = await getDebugLogs(id)
        return res.data.logs || []
    } catch (err) {
        return []
    }
}

// 运行调试
async function runDebugData(data) {
    try {
        await runDebug(data)
        alert('调试任务启动成功')
    } catch (err) {
        alert('调试任务启动失败')
    }
}
</script>
<style scoped>
/* 可根据需要自定义样式 */
</style> 