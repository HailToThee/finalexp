<template>
  <div>
    <h2>组织管理</h2>
    <input v-model="orgName" placeholder="新组织名" />
    <button @click="createOrg">创建组织</button>
    <ul>
      <li v-for="org in orgs" :key="org">{{ org }}</li>
    </ul>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const orgName = ref('')
const orgs = ref([])

const createOrg = async () => {
  await axios.post('/api/org/create', { org_name: orgName.value })
  fetchOrgs()
}

const fetchOrgs = async () => {
  // 这里假设有/api/org/list接口返回所有组织名
  const res = await axios.get('/api/org/list')
  orgs.value = res.data.orgs
}

onMounted(fetchOrgs)
</script>
