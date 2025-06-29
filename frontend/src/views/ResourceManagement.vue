<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">资源与组织管理</h2>
    <div class="mb-4 flex items-center">
      <button @click="orgDialog=true" class="bg-blue-500 text-white px-4 py-1 rounded mr-2">+ 新建组织</button>
      <button @click="quotaDialog=true" class="bg-green-500 text-white px-4 py-1 rounded">+ 配置资源配额</button>
    </div>
    <div class="mb-6">
      <h3 class="font-bold mb-2">组织结构</h3>
      <ul class="border rounded p-4 bg-white">
        <li v-for="org in orgs" :key="org.id" class="mb-2">
          <span class="font-semibold">{{ org.name }}</span>（配额：CPU {{ org.cpu_quota }}核，内存 {{ org.mem_quota }}GB，GPU {{ org.gpu_quota }}块）
          <span class="text-xs text-gray-500 ml-2">状态：{{ org.status }}</span>
        </li>
      </ul>
    </div>
    <div>
      <h3 class="font-bold mb-2">资源分配与优化</h3>
      <table class="min-w-full bg-white border">
        <thead>
          <tr>
            <th class="border px-4 py-2">组织</th>
            <th class="border px-4 py-2">CPU(核)</th>
            <th class="border px-4 py-2">内存(GB)</th>
            <th class="border px-4 py-2">GPU(块)</th>
            <th class="border px-4 py-2">已用CPU</th>
            <th class="border px-4 py-2">已用内存</th>
            <th class="border px-4 py-2">已用GPU</th>
            <th class="border px-4 py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="org in orgs" :key="org.id">
            <td class="border px-4 py-2">{{ org.name }}</td>
            <td class="border px-4 py-2">{{ org.cpu_quota }}</td>
            <td class="border px-4 py-2">{{ org.mem_quota }}</td>
            <td class="border px-4 py-2">{{ org.gpu_quota }}</td>
            <td class="border px-4 py-2">{{ org.cpu_used }}</td>
            <td class="border px-4 py-2">{{ org.mem_used }}</td>
            <td class="border px-4 py-2">{{ org.gpu_used }}</td>
            <td class="border px-4 py-2">
              <button @click="releaseResource(org.id)" class="text-red-500 text-sm">释放资源</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- 新建组织弹窗 -->
    <div v-if="orgDialog" class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded shadow-lg w-96">
        <h3 class="text-lg font-bold mb-2">新建组织</h3>
        <input v-model="newOrg.name" placeholder="组织名称" class="border w-full mb-2 px-2 py-1" />
        <button @click="createOrg" class="bg-blue-500 text-white px-4 py-1 rounded mr-2">确定</button>
        <button @click="orgDialog=false" class="bg-gray-300 px-4 py-1 rounded">取消</button>
      </div>
    </div>
    <!-- 配置资源配额弹窗 -->
    <div v-if="quotaDialog" class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded shadow-lg w-96">
        <h3 class="text-lg font-bold mb-2">配置资源配额</h3>
        <select v-model="quota.org_id" class="border w-full mb-2 px-2 py-1">
          <option disabled value="">请选择组织</option>
          <option v-for="org in orgs" :key="org.id" :value="org.id">{{ org.name }}</option>
        </select>
        <input v-model.number="quota.cpu_quota" placeholder="CPU(核)" type="number" class="border w-full mb-2 px-2 py-1" />
        <input v-model.number="quota.mem_quota" placeholder="内存(GB)" type="number" class="border w-full mb-2 px-2 py-1" />
        <input v-model.number="quota.gpu_quota" placeholder="GPU(块)" type="number" class="border w-full mb-2 px-2 py-1" />
        <button @click="setQuota" class="bg-green-500 text-white px-4 py-1 rounded mr-2">确定</button>
        <button @click="quotaDialog=false" class="bg-gray-300 px-4 py-1 rounded">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchOrgs, createOrg, setQuota, releaseResource } from '@/api.js'

const orgDialog = ref(false)
const newOrg = ref({ name: '' })
const quotaDialog = ref(false)
const quota = ref({ org_id: '', cpu_quota: 0, mem_quota: 0, gpu_quota: 0 })
const orgs = ref([])

// 获取组织列表
async function fetchOrgsData() {
  try {
    const res = await fetchOrgs()
    orgs.value = res.data.orgs || []
  } catch (e) {
    orgs.value = []
  }
}

onMounted(() => {
  fetchOrgsData()
})

// 新建组织
async function createOrgData() {
  try {
    await createOrg(newOrg.value)
    await fetchOrgsData()
    orgDialog.value = false
    newOrg.value = { name: '' }
    alert('组织创建成功')
  } catch (err) {
    alert('组织创建失败')
  }
}

// 配置资源配额
async function setQuotaData(orgId, quotaData) {
  try {
    await setQuota({
      org_id: orgId,
      ...quotaData
    })
    alert('资源配额设置成功')
  } catch (err) {
    alert('资源配额设置失败')
  }
}

// 释放资源
async function releaseResourceData(orgId) {
  try {
    await releaseResource({ org_id: orgId })
    alert('资源释放成功')
  } catch (err) {
    alert('资源释放失败')
  }
}
</script>

<style scoped>
/* 可根据需要自定义样式 */
</style> 