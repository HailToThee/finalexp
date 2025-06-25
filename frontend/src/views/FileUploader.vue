<template>
    <div class="container mx-auto p-4">
        <h2 class="text-xl font-bold">File Management</h2>
        <div id="uploader-container">
            <div id="picker">Select Files</div>
            <button id="start-upload" class="bg-blue-500 text-white px-4 py-2 rounded">Start Upload</button>
        </div>
    </div>
</template>
<script>
import WebUploader from 'webuploader'
export default {
    mounted() {
        this.initUploader()
    },
    methods: {
        initUploader() {
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
        },
    },
}
</script>