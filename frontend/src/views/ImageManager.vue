<template>
  <div>
    <h2>镜像管理</h2>
    <input v-model="searchQuery" placeholder="搜索镜像" />
    <button @click="searchImages">搜索</button>
    <ul>
      <li v-for="img in images" :key="img.name+img.tag">
        {{ img.name }}:{{ img.tag }}
        <button @click="pullImage(img.name, img.tag)">拉取</button>
        <button @click="deleteImage(img.name, img.tag)">删除</button>
      </li>
    </ul>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const searchQuery = ref('')
const images = ref([])

const searchImages = async () => {
  const res = await axios.get('/api/images/search', { params: { query: searchQuery.value } })
  images.value = res.data.images.map(i => {
    const [name, tag] = i.split(':')
    return { name, tag }
  })
}

const pullImage = async (name, tag) => {
  await axios.post('/api/images/pull', { name, tag })
  listImages()
}

const deleteImage = async (name, tag) => {
  await axios.delete('/api/images/delete', { data: { name, tag } })
  listImages()
}

const listImages = async () => {
  const res = await axios.get('/api/images/list')
  images.value = res.data.images
}

onMounted(listImages)
</script>