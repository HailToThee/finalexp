<template>
  <div>
    <h2>资源配额配置</h2>
    <select v-model="orgName">
      <option v-for="org in orgs" :key="org" :value="org">{{ org }}</option>
    </select>
    <input v-model="cpu" placeholder="CPU" />
    <input v-model="memory" placeholder="内存" />
    <input v-model="gpu" placeholder="GPU" />
    <button @click="setQuota">设置配额</button>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const orgs = ref([])
const orgName = ref('')
const cpu = ref('')
const memory = ref('')
const gpu = ref('')

const setQuota = async () => {
  await axios.post('/api/org/quota', {
    org_name: orgName.value, cpu: cpu.value, memory: memory.value, gpu: gpu.value
  })
}

const fetchOrgs = async () => {
  // 这里假设有/api/org/list接口返回所有组织名
  const res = await axios.get('/api/org/list')
  orgs.value = res.data.orgs
}

onMounted(fetchOrgs)
</script>
