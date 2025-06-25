<template>
  <div class="p-6 font-sans text-gray-800 max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold mb-6 text-center">AI 模型安全性评估平台</h1>

    <section class="mb-8">
      <h2 class="text-xl font-semibold mb-2">1. 用户登录 / 注册</h2>
      <input v-model="username" placeholder="用户名" class="border px-2 py-1 mr-2" />
      <input v-model="password" placeholder="密码" type="password" class="border px-2 py-1 mr-2" />
      <button @click="login" class="bg-blue-500 text-white px-4 py-1 rounded">登录</button>
      <button @click="register" class="bg-gray-500 text-white px-4 py-1 rounded ml-2">注册</button>
      <div class="text-green-600 mt-2" v-if="authMessage">{{ authMessage }}</div>
    </section>

    <section class="mb-8">
      <h2 class="text-xl font-semibold mb-2">2. 样本上传</h2>
      <input type="file" @change="uploadSample" class="mb-2" />
      <div v-if="uploadResult" class="text-green-600">{{ uploadResult }}</div>
    </section>

    <section class="mb-8">
      <h2 class="text-xl font-semibold mb-2">3. 模型列表</h2>
      <ul class="list-disc list-inside">
        <li v-for="model in modelList" :key="model">{{ model }}</li>
      </ul>
    </section>

    <section class="mb-8">
      <h2 class="text-xl font-semibold mb-2">4. 模型评估</h2>
      <input v-model="modelToEvaluate" placeholder="模型名" class="border px-2 py-1 mr-2" />
      <button @click="evaluateModel" class="bg-purple-600 text-white px-4 py-1 rounded">开始评估</button>
      <div v-if="evaluationResult" class="mt-2 bg-gray-100 p-3">
        <div>准确率: {{ evaluationResult.accuracy }}</div>
        <div>鲁棒性: {{ evaluationResult.robustness }}</div>
        <div>攻击成功率: {{ evaluationResult.asr }}</div>
      </div>
    </section>

    <section>
      <h2 class="text-xl font-semibold mb-2">5. 对抗样本攻击任务</h2>
      <button @click="runAttack" class="bg-red-500 text-white px-4 py-1 rounded">启动 FGSM 攻击</button>
      <div v-if="attackResult" class="mt-2 text-blue-600">{{ attackResult }}</div>
    </section>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'

const username = ref('')
const password = ref('')
const authMessage = ref('')
const uploadResult = ref('')
const modelList = ref([])
const modelToEvaluate = ref('')
const evaluationResult = ref(null)
const attackResult = ref('')

const login = async () => {
  const form = new FormData()
  form.append('username', username.value)
  form.append('password', password.value)
  const res = await axios.post('/api/auth/login', form)
  localStorage.setItem('token', res.data.access_token)
  authMessage.value = `欢迎 ${username.value}`
}

const register = async () => {
  const res = await axios.post('/api/auth/register', {
    username: username.value,
    password: password.value,
  })
  authMessage.value = res.data.msg
}

const uploadSample = async (event) => {
  const file = event.target.files[0]
  const formData = new FormData()
  formData.append('file', file)
  const res = await axios.post('/api/sample/upload', formData)
  uploadResult.value = res.data.message
}

const evaluateModel = async () => {
  const token = localStorage.getItem('token')
  const res = await axios.post('/api/model/evaluate', { model_name: modelToEvaluate.value }, {
    headers: { token }
  })
  evaluationResult.value = res.data
}

const runAttack = async () => {
  const token = localStorage.getItem('token')
  const res = await axios.post('/api/attack/fgsm', {
    model_path: modelToEvaluate.value,
    sample_path: '示例路径.png',
    epsilon: 0.1
  }, {
    headers: { token }
  })
  attackResult.value = res.data.msg
}

onMounted(async () => {
  const res = await axios.get('/api/model/list')
  modelList.value = res.data.models
})
</script>

<style scoped>
body {
  font-family: sans-serif;
  background: #f9f9f9;
}
</style>