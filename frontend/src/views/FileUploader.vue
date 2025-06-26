<template>
    <div class="container mx-auto p-4">
        <h2 class="text-xl font-bold">File Management</h2>
        <div id="uploader-container">
            <div id="picker">Select Files</div>
            <button id="start-upload" class="bg-blue-500 text-white px-4 py-2 rounded">Start Upload</button>
        </div>
        <input type="file" @change="onFileChange" />
        <button @click="uploadFile">上传</button>
        <ul>
            <li v-for="file in files" :key="file" @click="showInfo(file)">
                {{ file }}
            </li>
        </ul>
        <div v-if="fileInfo">
            <p>大小: {{ fileInfo.size }}</p>
            <p>类型: {{ fileInfo.type }}</p>
            <p>创建时间: {{ fileInfo.ctime }}</p>
            <p>修改时间: {{ fileInfo.mtime }}</p>
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import WebUploader from 'webuploader'

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

const initUploader = () => {
    const uploader = new WebUploader.create({
        server: '/api/file/upload',
        pick: '#picker',
        chunked: true,
        chunkSize: 5 * 1024 * 1024, // 5MB chunks
        threads: 1,
        fileVal: 'file',
        formData: {
            token: localStorage.getItem('token'),
        },
    })
    uploader.on('fileQueued', (file) => {
        console.log('File queued:', file.name)
        uploader.option('formData', {
            file_id: file.id,
            total_chunks: Math.ceil(file.size / (5 * 1024 * 1024)),
        })
    })
    uploader.on('uploadProgress', (file, percentage) => {
        console.log('Upload progress:', percentage * 100)
    })
    uploader.on('uploadSuccess', (file, response) => {
        console.log('Upload success:', response)
    })
    uploader.on('uploadError', (file, reason) => {
        console.error('Upload error:', reason)
    })
    document.getElementById('start-upload').addEventListener('click', () => {
        uploader.upload()
    })
}
</script>