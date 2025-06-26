<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">📁 文件管理</h2>
    <input type="file" @change="onFileChange" class="mb-4" />
    <button @click="uploadFile" class="mb-4">上传</button>
    <div class="text-green-600" v-if="uploadMsg">{{ uploadMsg }}</div>
    <ul class="mt-4">
      <li v-for="file in files" :key="file" @click="showInfo(file)" class="mb-1">{{ file }}</li>
    </ul>
    <div v-if="fileInfo" class="mt-4">
      <p>大小: {{ fileInfo.size }}</p>
      <p>类型: {{ fileInfo.type }}</p>
      <p>创建时间: {{ fileInfo.ctime }}</p>
      <p>修改时间: {{ fileInfo.mtime }}</p>
    </div>
  </div>
</template>
<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'

const uploadMsg = ref('')
const files = ref([])
const file = ref(null)
const fileInfo = ref(null)

const fetchFiles = async () => {
  const res = await axios.get('/api/files/list')
  files.value = res.data.files
}

const onFileChange = (e) => {
  file.value = e.target.files[0]
}

const uploadFile = async () => {
  const form = new FormData()
  form.append('file', file.value)
  await axios.post('/api/files/upload', form)
  fetchFiles()
}

const showInfo = async (filename) => {
  const res = await axios.get('/api/files/info', { params: { filename } })
  fileInfo.value = res.data
}

onMounted(fetchFiles)
</script>