<template>
  <div class="flex h-full">
    <!-- 仓库列表 -->
    <div class="w-64 bg-gray-50 border-r p-4 overflow-y-auto">
      <div class="flex justify-between items-center mb-2">
        <span class="font-bold">仓库({{ repos.length }}个)</span>
        <button @click="repoDialog=true" class="bg-blue-500 text-white px-2 py-1 rounded text-sm">+ 新建仓库</button>
      </div>
      <div v-for="repo in repos" :key="repo.id" @click="selectRepo(repo)" :class="['p-2 mb-2 rounded cursor-pointer', selectedRepo && selectedRepo.id===repo.id ? 'bg-blue-100' : 'hover:bg-gray-100']">
        <div class="font-semibold">名称: {{ repo.name }}</div>
        <div class="text-xs text-gray-500">镜像数: {{ repo.image_count }}</div>
        <div class="text-xs text-gray-500">类型: {{ repo.type }}</div>
      </div>
    </div>
    <!-- 镜像卡片区 -->
    <div class="flex-1 p-6 overflow-y-auto">
      <div class="flex items-center mb-4">
        <input v-model="searchKeyword" @keyup.enter="fetchImages" placeholder="请输入镜像名称" class="border rounded px-2 py-1 mr-2" />
        <button @click="fetchImages" class="bg-blue-500 text-white px-4 py-1 rounded mr-2">查询</button>
        <button @click="resetSearch" class="bg-gray-300 px-4 py-1 rounded mr-2">重置</button>
        <button @click="imageDialog=true" class="bg-green-500 text-white px-4 py-1 rounded mr-2">+ 新建镜像</button>
        <button @click="openPushDialog" class="bg-purple-500 text-white px-4 py-1 rounded">推送管理</button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div v-for="image in images" :key="image.id" class="bg-white rounded shadow p-4 relative">
          <div class="font-bold text-blue-700 mb-1">{{ image.name }}</div>
          <div class="text-xs text-gray-500 mb-1">版本: {{ image.version }}</div>
          <div class="text-xs text-gray-500 mb-1">仓库: {{ image.repo_name }}</div>
          <div class="text-xs text-gray-500 mb-1">下载数: {{ image.downloads }}</div>
          <div class="text-xs text-gray-500 mb-1">大小: {{ formatSize(image.file_size) }}</div>
          <div class="text-xs text-gray-500 mb-1">创建时间: {{ image.createdAt }}</div>
          <div class="flex items-center mt-2 space-x-2">
            <button @click="showDetailData(image.id)" class="text-blue-500 hover:underline">详情</button>
            <button @click="showPermissionData(image.id)" class="text-green-500 hover:underline">权限</button>
            <button @click="pushImageData(image.id)" class="text-purple-500 hover:underline">推送</button>
            <button v-if="image.permission === 'public'" @click="downloadImageData(image.id, image.name, image.version)" class="text-orange-500 hover:underline">下载</button>
            <button @click="deleteImageData(image.id)" class="text-red-500 hover:underline">删除</button>
          </div>
        </div>
      </div>
    </div>
    <!-- 新建仓库弹窗 -->
    <div v-if="repoDialog" class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded shadow-lg w-96">
        <h3 class="text-lg font-bold mb-2">新建仓库</h3>
        <input v-model="newRepo.name" placeholder="仓库名称" class="border w-full mb-2 px-2 py-1" />
        <input v-model="newRepo.type" placeholder="类型(如x86/arm)" class="border w-full mb-2 px-2 py-1" />
        <button @click="createRepoData" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">确定</button>
        <button @click="repoDialog=false" class="bg-gray-300 px-4 py-1 rounded">取消</button>
      </div>
    </div>
    <!-- 新建镜像弹窗（多步） -->
    <div v-if="imageDialog" class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded shadow-lg w-[30rem]">
        <h3 class="text-lg font-bold mb-2">新建镜像</h3>
        <div v-if="imageStep===1">
          <div class="mb-2">第一步，导入文件</div>
          <input type="file" @change="handleFileChange" class="mb-2" />
          <button @click="imageStep=2" :disabled="!selectedFile" class="bg-blue-500 text-white px-4 py-1 rounded">下一步</button>
        </div>
        <div v-else>
          <div class="mb-2">第二步，新建镜像</div>
          <input v-model="newImage.name" placeholder="镜像名称" class="border w-full mb-2 px-2 py-1" />
          <select v-model="newImage.repo_id" class="border w-full mb-2 px-2 py-1">
            <option disabled value="">请选择仓库</option>
            <option v-for="repo in repos" :key="repo.id" :value="repo.id">{{ repo.name }}</option>
          </select>
          <input v-model="newImage.version" placeholder="镜像版本" class="border w-full mb-2 px-2 py-1" />
          <button @click="createImage" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">创建镜像</button>
          <button @click="imageStep=1" class="bg-gray-300 px-4 py-1 rounded">上一步</button>
        </div>
        <button @click="closeImageDialog" class="absolute top-2 right-2 text-gray-400">×</button>
      </div>
    </div>
    <!-- 镜像详情弹窗 -->
    <div v-if="detailDialog" class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded shadow-lg w-96">
        <h3 class="text-lg font-bold mb-2">镜像详情</h3>
        <div v-if="imageDetail">
          <p><b>名称:</b> {{ imageDetail.name }}</p>
          <p><b>版本:</b> {{ imageDetail.version }}</p>
          <p><b>仓库:</b> {{ imageDetail.repo_name }}</p>
          <p><b>下载数:</b> {{ imageDetail.downloads }}</p>
          <p><b>大小:</b> {{ imageDetail.size }}</p>
          <p><b>创建时间:</b> {{ imageDetail.createdAt }}</p>
          <p><b>状态:</b> {{ imageDetail.status }}</p>
          <p><b>用途:</b> {{ imageDetail.usage }}</p>
          <button v-if="imageDetail.permission === 'public'" @click="downloadImageData(imageDetail.id, imageDetail.name, imageDetail.version)" class="bg-orange-500 text-white px-4 py-1 rounded">下载</button>
        </div>
        <button @click="detailDialog = false" class="mt-4 bg-gray-300 px-4 py-1 rounded">关闭</button>
      </div>
    </div>
    <!-- 权限管理弹窗 -->
    <div v-if="permissionDialog" class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded shadow-lg w-96">
        <h3 class="text-lg font-bold mb-2">权限管理</h3>
        <div v-if="imageDetail">
          <select v-model="imageDetail.permission" class="border w-full mb-2 px-2 py-1">
            <option value="public">公开</option>
            <option value="private">私有</option>
          </select>
          <button @click="updatePermissionData" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">更新权限</button>
        </div>
        <button @click="permissionDialog = false" class="mt-4 bg-gray-300 px-4 py-1 rounded">关闭</button>
      </div>
    </div>
    <!-- 推送管理弹窗 -->
    <div v-if="pushDialog" class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded shadow-lg w-[40rem] max-h-[80vh] overflow-y-auto">
        <h3 class="text-lg font-bold mb-4">推送管理</h3>
        
        <!-- 远程仓库状态 -->
        <div class="mb-6 p-4 bg-gray-50 rounded">
          <h4 class="font-semibold mb-2">远程仓库状态</h4>
          <div v-if="pushStatus" class="grid grid-cols-2 gap-4 text-sm">
            <div><b>仓库名称:</b> {{ pushStatus.repository?.name || 'FINAL_EXP_Remote_Repository' }}</div>
            <div><b>状态:</b> {{ pushStatus.repository?.status || 'active' }}</div>
            <div><b>总镜像数:</b> {{ pushStatus.statistics?.total_images || 0 }}</div>
            <div><b>总大小:</b> {{ pushStatus.statistics?.total_size || '0B' }}</div>
            <div><b>推送次数:</b> {{ pushStatus.statistics?.push_count || 0 }}</div>
            <div><b>最后推送:</b> {{ pushStatus.statistics?.last_push || '无' }}</div>
          </div>
          <div v-else class="text-gray-500">加载中...</div>
        </div>
        
        <!-- 推送历史 -->
        <div>
          <h4 class="font-semibold mb-2">推送历史</h4>
          <div v-if="pushHistory.length > 0" class="space-y-2">
            <div v-for="record in pushHistory" :key="record.id" class="p-3 border rounded bg-white">
              <div class="flex justify-between items-start">
                <div class="flex-1">
                  <div class="font-medium">{{ record.image_name }} v{{ record.image_version }}</div>
                  <div class="text-sm text-gray-600">
                    推送者: {{ record.pushed_by }} | 
                    时间: {{ new Date(record.pushed_at).toLocaleString() }} | 
                    文件: {{ record.remote_filename }}
                  </div>
                </div>
                <span class="text-xs px-2 py-1 rounded" :class="record.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                  {{ record.status === 'success' ? '成功' : '失败' }}
                </span>
              </div>
            </div>
          </div>
          <div v-else class="text-gray-500 text-center py-4">暂无推送记录</div>
        </div>
        
        <button @click="pushDialog = false" class="mt-4 bg-gray-300 px-4 py-1 rounded">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchRepos, fetchImages, uploadImage, deleteImage, getImageDetail, pushImage, createRepo, updatePermission, downloadImage, getPushHistory, getPushStatus } from '@/api.js'

const repos = ref([])
const selectedRepo = ref(null)
const images = ref([])
const searchKeyword = ref('')
const repoDialog = ref(false)
const newRepo = ref({ name: '', type: '' })
const imageDialog = ref(false)
const imageStep = ref(1)
const selectedFile = ref(null)
const newImage = ref({ name: '', repo_id: '', version: '' })
const detailDialog = ref(false)
const imageDetail = ref(null)
const permissionDialog = ref(false)
const pushDialog = ref(false)
const pushHistory = ref([])
const pushStatus = ref(null)

async function fetchReposData() {
  try {
    const res = await fetchRepos()
    repos.value = res.data.repos || []
    if (!selectedRepo.value && repos.value.length) selectedRepo.value = repos.value[0]
  } catch (e) {
    repos.value = []
  }
}

function selectRepo(repo) {
  selectedRepo.value = repo
  fetchImagesData()
}

async function fetchImagesData() {
  const params = { keyword: searchKeyword.value }
  if (selectedRepo.value) params.repo_id = selectedRepo.value.id
  try {
    const res = await fetchImages(params)
    images.value = res.data.images || []
  } catch (e) {
    images.value = []
  }
}

function resetSearch() {
  searchKeyword.value = ''
  fetchImagesData()
}

async function createRepoData() {
  try {
    await createRepo(newRepo.value)
    repoDialog.value = false
    newRepo.value = { name: '', type: '' }
    await fetchReposData()
    alert('仓库创建成功')
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      alert('仓库创建失败: ' + err.response.data.detail)
    } else if (err.message) {
      alert('仓库创建失败: ' + err.message)
    } else {
      alert('仓库创建失败')
    }
  }
}

function handleFileChange(e) {
  const file = e.target.files[0];
  if (!file) return;
  const allowed = [
    '.img', '.tar', '.tar.gz'
  ];
  // 支持tar.gz双后缀判断
  const name = file.name.toLowerCase();
  const isValid = allowed.some(ext => name.endsWith(ext));
  if (!isValid) {
    alert('只支持导入img、tar或者tar.gz文件');
    e.target.value = '';
    selectedFile.value = null;
    return;
  }
  selectedFile.value = file;
}

function closeImageDialog() {
  imageDialog.value = false
  imageStep.value = 1
  selectedFile.value = null
  newImage.value = { name: '', repo_id: '', version: '' }
}

async function createImage() {
  if (!selectedFile.value) return
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('name', newImage.value.name)
  formData.append('repo_id', newImage.value.repo_id)
  formData.append('version', newImage.value.version)
  try {
    await uploadImage(formData)
    closeImageDialog()
    await fetchImagesData()
    alert('镜像上传成功')
  } catch (err) {
    // 显示具体的错误信息
    if (err.response && err.response.data && err.response.data.detail) {
      alert('镜像上传失败: ' + err.response.data.detail)
    } else if (err.message) {
      alert('镜像上传失败: ' + err.message)
    } else {
      alert('镜像上传失败，请检查网络连接')
    }
  }
}

async function deleteImageData(id) {
  if (!confirm('确定要删除该镜像吗？')) return
  try {
    await deleteImage(id)
    await fetchImagesData()
    alert('镜像删除成功')
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      alert('镜像删除失败: ' + err.response.data.detail)
    } else if (err.message) {
      alert('镜像删除失败: ' + err.message)
    } else {
      alert('镜像删除失败')
    }
  }
}

async function showDetailData(id) {
  try {
    const res = await getImageDetail(id)
    imageDetail.value = res.data
    detailDialog.value = true
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      alert('获取镜像详情失败: ' + err.response.data.detail)
    } else if (err.message) {
      alert('获取镜像详情失败: ' + err.message)
    } else {
      alert('获取镜像详情失败')
    }
  }
}

async function showPermissionData(id) {
  try {
    const res = await getImageDetail(id)
    imageDetail.value = res.data
    permissionDialog.value = true
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      alert('获取镜像权限失败: ' + err.response.data.detail)
    } else if (err.message) {
      alert('获取镜像权限失败: ' + err.message)
    } else {
      alert('获取镜像权限失败')
    }
  }
}

async function updatePermissionData() {
  try {
    await updatePermission({ id: imageDetail.value.id, permission: imageDetail.value.permission })
    permissionDialog.value = false
    await fetchImagesData()
    alert('权限更新成功')
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      alert('权限更新失败: ' + err.response.data.detail)
    } else if (err.message) {
      alert('权限更新失败: ' + err.message)
    } else {
      alert('权限更新失败')
    }
  }
}

async function pushImageData(id) {
  try {
    await pushImage({ id })
    alert('推送成功')
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      alert('推送失败: ' + err.response.data.detail)
    } else if (err.message) {
      alert('推送失败: ' + err.message)
    } else {
      alert('推送失败')
    }
  }
}

async function downloadImageData(id, name, version) {
  try {
    const res = await downloadImage(id)
    const blob = new Blob([res.data])
    // 尝试从header获取文件名后缀
    let ext = 'tar';
    const disposition = res.headers['content-disposition']
    if (disposition) {
      const match = disposition.match(/filename=.*\.(\w+)/)
      if (match) ext = match[1]
    }
    const filename = `${name}-${version}.${ext}`
    const link = document.createElement('a')
    link.href = window.URL.createObjectURL(blob)
    link.download = filename
    link.click()
    window.URL.revokeObjectURL(link.href)
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      alert('下载失败: ' + err.response.data.detail)
    } else if (err.message) {
      alert('下载失败: ' + err.message)
    } else {
      alert('下载失败，可能无权限或文件不存在')
    }
  }
}

async function fetchPushData() {
  try {
    const [historyRes, statusRes] = await Promise.all([
      getPushHistory(),
      getPushStatus()
    ])
    pushHistory.value = historyRes.data.push_history || []
    pushStatus.value = statusRes.data
  } catch (err) {
    console.error('获取推送数据失败:', err)
    pushHistory.value = []
    pushStatus.value = null
  }
}

function formatSize(size) {
  if (size == null || isNaN(size)) return '-';
  if (size < 1024) return size + ' B';
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB';
  if (size < 1024 * 1024 * 1024) return (size / 1024 / 1024).toFixed(1) + ' MB';
  return (size / 1024 / 1024 / 1024).toFixed(2) + ' GB';
}

function openPushDialog() {
  fetchPushData()
  pushDialog.value = true
}

onMounted(() => {
  fetchReposData().then(() => {
    if (repos.value.length) {
      selectedRepo.value = repos.value[0]
      fetchImagesData()
    }
  })
})
</script>

<style scoped>
/* 可根据需要自定义样式 */
</style> 