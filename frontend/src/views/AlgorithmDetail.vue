<template>
  <div class="p-8 bg-gray-50 min-h-screen">
    <div class="max-w-7xl mx-auto">
      <!-- 算法基本信息 -->
      <div class="bg-white rounded-xl shadow p-8 flex items-center justify-between mb-6">
        <div>
          <h2 class="text-2xl font-bold mb-2">{{ algo.name }} <span class="ml-2 text-sm text-gray-400">{{ algo.version }}</span></h2>
          <div class="text-gray-600 mb-1">{{ algo.desc }}</div>
          <div class="space-x-2">
            <span v-for="tag in algo.tags" :key="tag" class="inline-block bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs">{{ tag }}</span>
          </div>
        </div>
        <div class="space-x-2">
          <el-select v-model="algo.version" placeholder="切换版本" size="small" style="width:120px">
            <el-option v-for="v in algo.versions" :key="v" :label="v" :value="v" />
          </el-select>
          <el-button size="small" @click="subscribe">{{ algo.subscribed ? '取消订阅' : '订阅' }}</el-button>
          <el-button size="small" @click="cloneAlgo">克隆</el-button>
          <el-button size="small" type="danger" @click="deleteAlgo">删除</el-button>
        </div>
      </div>
      <!-- Tab切换 -->
      <el-tabs v-model="activeTab">
        <el-tab-pane label="目录结构" name="structure">
          <div class="flex gap-6">
            <!-- 目录树 -->
            <el-tree :data="algo.structure" :props="treeProps" class="w-64 bg-gray-50 p-4 rounded" @node-click="selectFile" :expand-on-click-node="false" ref="treeRef" @node-contextmenu="handleTreeContextMenu" />
            <!-- 文件内容编辑区 -->
            <div class="flex-1 bg-white rounded shadow p-4">
              <div class="mb-2 text-gray-500 flex items-center justify-between">
                <span>{{ selectedFile.name }}</span>
                <el-upload :show-file-list="false" :auto-upload="false" :before-upload="handleFileUpload">
                  <el-button size="mini">上传文件</el-button>
                </el-upload>
              </div>
              <el-input v-model="selectedFile.content" type="textarea" rows="18" />
              <div class="mt-2 text-right">
                <el-button size="small" type="primary" @click="saveFile">保存</el-button>
              </div>
            </div>
          </div>
          <!-- 右键菜单 -->
          <el-dropdown v-if="contextMenuVisible" :style="{position:'fixed',left:contextMenuX+'px',top:contextMenuY+'px',zIndex:9999}" @command="handleContextMenuCommand" @visible-change="v=>!v && (contextMenuVisible=false)">
            <span></span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="newFile">新建文件</el-dropdown-item>
              <el-dropdown-item command="newFolder">新建文件夹</el-dropdown-item>
              <el-dropdown-item command="rename">重命名</el-dropdown-item>
              <el-dropdown-item command="delete">删除</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </el-tab-pane>
        <el-tab-pane label="训练任务" name="train">
          <div class="mb-4 flex justify-between items-center">
            <el-button type="primary" @click="trainDialog=true">新建训练任务</el-button>
          </div>
          <el-table :data="trainTasks" style="width:100%">
            <el-table-column prop="name" label="任务名称" />
            <el-table-column prop="status" label="状态" width="100" />
            <el-table-column prop="progress" label="进度" width="120" />
            <el-table-column prop="createdAt" label="创建时间" width="160" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="mini" @click="viewTrainTask(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="评测任务" name="eval">
          <div class="mb-4 flex justify-between items-center">
            <el-button type="primary" @click="evalDialog=true">新建评测任务</el-button>
          </div>
          <el-table :data="evalTasks" style="width:100%">
            <el-table-column prop="name" label="任务名称" />
            <el-table-column prop="status" label="状态" width="100" />
            <el-table-column prop="progress" label="进度" width="120" />
            <el-table-column prop="createdAt" label="创建时间" width="160" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="mini" @click="viewEvalTask(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="版本历史" name="history">
          <el-timeline>
            <el-timeline-item v-for="v in algo.versions" :key="v" :timestamp="v" placement="top">
              <span>{{ v }}</span>
            </el-timeline-item>
          </el-timeline>
        </el-tab-pane>
        <el-tab-pane label="日志" name="log">
          <el-table :data="debugLogs" style="width:100%">
            <el-table-column prop="time" label="时间" width="180" />
            <el-table-column prop="params" label="参数" />
            <el-table-column prop="asr" label="ASR" width="80" />
            <el-table-column prop="perturbation" label="扰动" width="80" />
            <el-table-column label="可视化" width="120">
              <template #default="{ row }">
                <img v-if="row.visualization" :src="row.visualization" alt="可视化" style="max-width:80px;max-height:40px;object-fit:contain;" />
                <span v-else class="text-gray-400">无</span>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
      <!-- 新建训练任务弹窗 -->
      <el-dialog :visible.sync="trainDialog" width="500px" title="新建训练任务">
        <el-form :model="trainForm" label-width="90px">
          <el-form-item label="任务名称" required>
            <el-input v-model="trainForm.name" />
          </el-form-item>
          <el-form-item label="数据集">
            <el-select v-model="trainForm.dataset" placeholder="请选择数据集">
              <el-option v-for="d in datasetList" :key="d" :label="d" :value="d" />
            </el-select>
          </el-form-item>
          <el-form-item label="参数配置">
            <el-input v-model="trainForm.params" type="textarea" rows="3" placeholder="如 batch_size=32, lr=0.001" />
          </el-form-item>
          <el-form-item label="资源分配">
            <el-select v-model="trainForm.resource" placeholder="请选择资源">
              <el-option label="CPU" value="CPU" />
              <el-option label="GPU" value="GPU" />
            </el-select>
          </el-form-item>
        </el-form>
        <div class="text-right mt-4">
          <el-button @click="trainDialog=false">取消</el-button>
          <el-button type="primary" @click="submitTrainTask">提交</el-button>
        </div>
      </el-dialog>
      <!-- 新建评测任务弹窗 -->
      <el-dialog :visible.sync="evalDialog" width="500px" title="新建评测任务">
        <el-form :model="evalForm" label-width="90px">
          <el-form-item label="任务名称" required>
            <el-input v-model="evalForm.name" />
          </el-form-item>
          <el-form-item label="评测集">
            <el-select v-model="evalForm.dataset" placeholder="请选择评测集">
              <el-option v-for="d in datasetList" :key="d" :label="d" :value="d" />
            </el-select>
          </el-form-item>
          <el-form-item label="参数配置">
            <el-input v-model="evalForm.params" type="textarea" rows="3" placeholder="如 batch_size=32, attack=fgsm" />
          </el-form-item>
        </el-form>
        <div class="text-right mt-4">
          <el-button @click="evalDialog=false">取消</el-button>
          <el-button type="primary" @click="submitEvalTask">提交</el-button>
        </div>
      </el-dialog>
      <!-- 训练任务详情弹窗 -->
      <el-dialog :visible.sync="trainTaskDetailDialog" width="600px" title="训练任务详情">
        <el-descriptions :title="trainTaskDetail.name" :column="2" border>
          <el-descriptions-item label="状态">{{ trainTaskDetail.status }}</el-descriptions-item>
          <el-descriptions-item label="进度">{{ trainTaskDetail.progress }}</el-descriptions-item>
          <el-descriptions-item label="参数">{{ trainTaskDetail.params }}</el-descriptions-item>
          <el-descriptions-item label="资源">{{ trainTaskDetail.resource }}</el-descriptions-item>
          <el-descriptions-item label="数据集">{{ trainTaskDetail.dataset }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ trainTaskDetail.createdAt }}</el-descriptions-item>
        </el-descriptions>
        <div class="mt-4">
          <div class="font-bold mb-2">日志</div>
          <el-input v-model="trainTaskDetail.log" type="textarea" rows="8" readonly />
        </div>
        <div class="text-right mt-4">
          <el-button @click="trainTaskDetailDialog=false">关闭</el-button>
        </div>
      </el-dialog>
      <!-- 评测任务详情弹窗 -->
      <el-dialog :visible.sync="evalTaskDetailDialog" width="600px" title="评测任务详情">
        <el-descriptions :title="evalTaskDetail.name" :column="2" border>
          <el-descriptions-item label="状态">{{ evalTaskDetail.status }}</el-descriptions-item>
          <el-descriptions-item label="进度">{{ evalTaskDetail.progress }}</el-descriptions-item>
          <el-descriptions-item label="参数">{{ evalTaskDetail.params }}</el-descriptions-item>
          <el-descriptions-item label="评测集">{{ evalTaskDetail.dataset }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ evalTaskDetail.createdAt }}</el-descriptions-item>
        </el-descriptions>
        <div class="mt-4">
          <div class="font-bold mb-2">日志</div>
          <el-input v-model="evalTaskDetail.log" type="textarea" rows="8" readonly />
        </div>
        <div class="text-right mt-4">
          <el-button @click="evalTaskDetailDialog=false">关闭</el-button>
        </div>
      </el-dialog>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAlgorithmTree, fetchAlgorithms, uploadAlgorithmFile, createAlgorithmFolder, deleteAlgorithmFile, renameAlgorithmFile, getAlgorithmInfo, getDebugLogs, runDebug } from '@/api.js'

const algo = ref({
  name: '', desc: '', tags: [], version: '', versions: [], subscribed: false, structure: [], log: ''
})
const activeTab = ref('structure')
const selectedFile = ref({ name: '', content: '' })
const treeProps = ref({ children: 'children', label: 'label' })
const trainDialog = ref(false)
const trainForm = ref({ name: '', dataset: '', params: '', resource: '' })
const trainTasks = ref([])
const evalDialog = ref(false)
const evalForm = ref({ name: '', dataset: '', params: '' })
const evalTasks = ref([])
const datasetList = ['IMDB', 'SST-2', '自定义数据集']
const trainTaskDetailDialog = ref(false)
const trainTaskDetail = ref({})
const evalTaskDetailDialog = ref(false)
const evalTaskDetail = ref({})
const contextMenuVisible = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const contextMenuNode = ref(null)
const debugLogs = ref([])

// 获取算法详情
async function getAlgorithmDetail(id) {
  try {
    const res = await getAlgorithmInfo(id)
    algo.value = {
      ...algo.value,
      name: res.data.name,
      desc: res.data.description,
      tags: res.data.type ? [res.data.type] : [],
      version: 'v1.0',
      versions: ['v1.0'],
      // 结构、订阅、日志等可后续对接
    }
  } catch (err) {
    // 处理错误
  }
}

// 获取调试日志
async function getDebugLogsData(id) {
  try {
    const res = await getDebugLogs(id)
    debugLogs.value = res.data.logs || []
    // 用于日志Tab和任务详情弹窗
    algo.value.log = debugLogs.value.map(l => `[${l.time}] ${l.params} ASR:${l.asr} 扰动:${l.perturbation}`).join('\n')
    // 训练/评测任务模拟填充
    trainTasks.value = debugLogs.value.map(l => ({
      name: '调试任务-' + l.time,
      status: '已完成',
      progress: '100%',
      createdAt: l.time,
      params: l.params,
      resource: 'GPU',
      dataset: 'IMDB',
      log: `ASR:${l.asr} 扰动:${l.perturbation}`
    }))
    evalTasks.value = trainTasks.value
  } catch (err) {
    // 处理错误
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

function subscribe() {
  algo.value.subscribed = !algo.value.subscribed
  alert(algo.value.subscribed ? '已订阅' : '已取消订阅')
}

function cloneAlgo() {
  alert('克隆成功')
}

function deleteAlgo() {
  alert('确定要删除该算法吗？')
}

function selectFile(node) {
  if (node.isLeaf) {
    selectedFile.value = node
  }
}

function saveFile() {
  alert('保存成功')
}

function viewTrainTask(row) {
  trainTaskDetail.value = row
  trainTaskDetailDialog.value = true
}

function submitTrainTask() {
  trainDialog.value = false
  alert('训练任务已提交')
}

function viewEvalTask(row) {
  evalTaskDetail.value = row
  evalTaskDetailDialog.value = true
}

function submitEvalTask() {
  evalDialog.value = false
  alert('评测任务已提交')
}

function handleTreeContextMenu(event, data, node, comp) {
  event.preventDefault();
  contextMenuVisible.value = true;
  contextMenuX.value = event.clientX;
  contextMenuY.value = event.clientY;
  contextMenuNode.value = data;
}

function handleContextMenuCommand(cmd) {
  if (!contextMenuNode.value) return;
  if (cmd === 'newFile') {
    const name = prompt('请输入新文件名');
    if (name) {
      (contextMenuNode.value.children = contextMenuNode.value.children || []).push({ label: name, name, content: '', isLeaf: true });
    }
  } else if (cmd === 'newFolder') {
    const name = prompt('请输入新文件夹名');
    if (name) {
      (contextMenuNode.value.children = contextMenuNode.value.children || []).push({ label: name, name, children: [] });
    }
  } else if (cmd === 'rename') {
    const name = prompt('请输入新名称', contextMenuNode.value.label);
    if (name) contextMenuNode.value.label = name;
  } else if (cmd === 'delete') {
    deleteNode(algo.value.structure, contextMenuNode.value);
  }
  contextMenuVisible.value = false;
}

function deleteNode(tree, node) {
  for (let i = 0; i < tree.length; i++) {
    if (tree[i] === node) {
      tree.splice(i, 1); return true;
    } else if (tree[i].children) {
      if (deleteNode(tree[i].children, node)) return true;
    }
  }
  return false;
}

function handleFileUpload(file) {
  // 简单模拟上传，实际应调用后端接口
  algo.value.structure.push({ label: file.name, name: file.name, content: '', isLeaf: true });
  alert('上传成功');
  return false;
}
</script>
<style scoped>
</style> 