<template>
  <div class="flex gap-6 p-8 bg-gray-50 min-h-screen">
    <!-- 左侧组织树 -->
    <aside class="w-64 bg-white rounded-xl shadow p-4 flex-shrink-0">
      <input type="text" v-model="orgSearch" placeholder="🔍 搜索组织/部门" class="w-full mb-4 px-3 py-2 border rounded focus:outline-none focus:ring" />
      <div class="text-gray-700 text-sm font-bold mb-2">顶级组织</div>
      <ul class="text-gray-600 text-sm space-y-1">
        <li>
          <span class="font-semibold cursor-pointer" :class="{ 'text-blue-600': selectedOrg==='武汉总部' }" @click="selectOrg('武汉总部')">武汉总部</span>
          <ul class="ml-4 space-y-1">
            <li :class="{ 'text-blue-600': selectedOrg==='武汉总部' }" class="cursor-pointer" @click="selectOrg('武汉总部')">武汉总部</li>
            <li>
              <span :class="{ 'text-blue-600': selectedOrg==='长沙分点' }" class="cursor-pointer" @click="selectOrg('长沙分点')">长沙分点</span>
              <ul class="ml-4 space-y-1">
                <li :class="{ 'text-blue-600': selectedOrg==='市场部门' }" class="cursor-pointer" @click="selectOrg('市场部门')">市场部门</li>
                <li :class="{ 'text-blue-600': selectedOrg==='财务部门' }" class="cursor-pointer" @click="selectOrg('财务部门')">财务部门</li>
              </ul>
            </li>
          </ul>
        </li>
        <li>
          <span class="font-semibold cursor-pointer" :class="{ 'text-blue-600': selectedOrg==='新部门' }" @click="selectOrg('新部门')">新部门</span>
          <ul class="ml-4 space-y-1">
            <li :class="{ 'text-blue-600': selectedOrg==='测试部门' }" class="cursor-pointer" @click="selectOrg('测试部门')">测试部门</li>
            <li :class="{ 'text-blue-600': selectedOrg==='测试2部门' }" class="cursor-pointer" @click="selectOrg('测试2部门')">测试2部门</li>
          </ul>
        </li>
      </ul>
    </aside>
    <!-- 右侧主内容区 -->
    <section class="flex-1">
      <!-- 顶部筛选区 -->
      <div class="bg-white rounded-xl shadow p-6 mb-6 flex flex-wrap gap-4 items-center">
        <input type="text" v-model="searchNickname" placeholder="用户昵称" class="px-3 py-2 border rounded focus:outline-none focus:ring w-40" />
        <input type="text" v-model="searchPhone" placeholder="手机号" class="px-3 py-2 border rounded focus:outline-none focus:ring w-40" />
        <select v-model="searchStatus" class="px-3 py-2 border rounded focus:outline-none focus:ring w-40">
          <option value="">用户状态</option>
          <option value="启用">启用</option>
          <option value="禁用">禁用</option>
        </select>
        <input type="date" v-model="searchDate" class="px-3 py-2 border rounded focus:outline-none focus:ring w-40" />
        <button class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600" @click="filterUsers">查询</button>
        <button class="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300" @click="resetFilters">重置</button>
        <button class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 ml-auto" @click="showAddForm=true">+ 新增</button>
      </div>
      <!-- 用户表格 -->
      <div class="bg-white rounded-xl shadow p-6">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-100">
            <tr>
              <th class="py-2 px-4 border-b">用户编号</th>
              <th class="py-2 px-4 border-b">用户昵称</th>
              <th class="py-2 px-4 border-b">用户名称</th>
              <th class="py-2 px-4 border-b">部门</th>
              <th class="py-2 px-4 border-b">手机号</th>
              <th class="py-2 px-4 border-b">状态</th>
              <th class="py-2 px-4 border-b">创建时间</th>
              <th class="py-2 px-4 border-b">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in pagedUsers" :key="user.id" class="hover:bg-blue-50">
              <td class="py-2 px-4 border-b">{{ user.id }}</td>
              <td class="py-2 px-4 border-b">{{ user.nickname }}</td>
              <td class="py-2 px-4 border-b">{{ user.username }}</td>
              <td class="py-2 px-4 border-b">{{ user.department }}</td>
              <td class="py-2 px-4 border-b">{{ user.phone }}</td>
              <td class="py-2 px-4 border-b">
                <span :class="user.status === '启用' ? 'text-green-600' : 'text-gray-400'">●</span> {{ user.status }}
              </td>
              <td class="py-2 px-4 border-b">{{ user.createdAt }}</td>
              <td class="py-2 px-4 border-b space-x-2">
                <button class="text-blue-500 hover:underline" @click="editUser(user)">编辑</button>
                <button class="text-red-500 hover:underline" @click="confirmDelete(user)">删除</button>
                <button class="text-gray-500 hover:underline">更多</button>
              </td>
            </tr>
            <tr v-if="pagedUsers.length === 0">
              <td colspan="8" class="text-center py-4 text-gray-400">暂无用户</td>
            </tr>
          </tbody>
        </table>
        <!-- 分页区 -->
        <div class="flex justify-between items-center mt-4 text-sm">
          <div>共 {{ filteredUsers.length }} 条</div>
          <div class="space-x-2">
            <button class="px-2" :disabled="page===1" @click="page--">上一页</button>
            <span>{{ page }}</span>
            <button class="px-2" :disabled="page===maxPage" @click="page++">下一页</button>
          </div>
        </div>
      </div>
      <!-- 新增/编辑弹窗表单 -->
      <div v-if="showAddForm || showEditForm" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-30 z-50">
        <div class="bg-white rounded-xl shadow-xl p-8 w-full max-w-xl relative">
          <button class="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl" @click="closeForm">×</button>
          <h2 class="text-2xl font-bold mb-6 text-center">{{ showAddForm ? '新增用户' : '编辑用户' }}</h2>
          <form @submit.prevent="showAddForm ? addUser() : updateUser()">
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label class="block text-gray-600 mb-1">用户昵称</label>
                <input v-model="form.nickname" type="text" class="w-full px-3 py-2 border rounded" required />
              </div>
              <div>
                <label class="block text-gray-600 mb-1">用户名称</label>
                <input v-model="form.username" type="text" class="w-full px-3 py-2 border rounded" required />
              </div>
              <div>
                <label class="block text-gray-600 mb-1">部门</label>
                <input v-model="form.department" type="text" class="w-full px-3 py-2 border rounded" required />
              </div>
              <div>
                <label class="block text-gray-600 mb-1">手机号</label>
                <input v-model="form.phone" type="text" class="w-full px-3 py-2 border rounded" required />
              </div>
              <div>
                <label class="block text-gray-600 mb-1">状态</label>
                <select v-model="form.status" class="w-full px-3 py-2 border rounded">
                  <option value="启用">启用</option>
                  <option value="禁用">禁用</option>
                </select>
              </div>
              <div>
                <label class="block text-gray-600 mb-1">创建时间</label>
                <input v-model="form.createdAt" type="datetime-local" class="w-full px-3 py-2 border rounded" required />
              </div>
            </div>
            <div class="flex justify-end gap-4">
              <button type="button" class="px-6 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" @click="closeForm">取消</button>
              <button type="submit" class="px-6 py-2 rounded bg-blue-600 text-white hover:bg-blue-700">确定</button>
            </div>
          </form>
        </div>
      </div>
      <!-- 删除确认弹窗 -->
      <div v-if="showDeleteConfirm" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-30 z-50">
        <div class="bg-white rounded-xl shadow-xl p-8 w-full max-w-sm relative">
          <div class="text-lg mb-6">确定要删除用户 <span class="font-bold text-red-600">{{ deleteTarget?.nickname }}</span> 吗？</div>
          <div class="flex justify-end gap-4">
            <button class="px-6 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" @click="showDeleteConfirm=false">取消</button>
            <button class="px-6 py-2 rounded bg-red-600 text-white hover:bg-red-700" @click="deleteUser">删除</button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
// 假数据
const allUsers = ref([
  { id: 1, nickname: 'admin', username: '管理员', department: '长沙分点', phone: '18812606277', status: '启用', createdAt: '2024-12-05T17:03' },
  { id: 2, nickname: 'dxy', username: 'xy', department: '市场部门', phone: '15601691311', status: '启用', createdAt: '2024-12-07T09:07' },
  { id: 3, nickname: 'test', username: '测试号1', department: '运营部门', phone: '15601691222', status: '禁用', createdAt: '2024-11-21T02:13' },
])
const orgSearch = ref('')
const selectedOrg = ref('')
const searchNickname = ref('')
const searchPhone = ref('')
const searchStatus = ref('')
const searchDate = ref('')
const page = ref(1)
const pageSize = 10
const showAddForm = ref(false)
const showEditForm = ref(false)
const showDeleteConfirm = ref(false)
const deleteTarget = ref(null)
const form = ref({ id: null, nickname: '', username: '', department: '', phone: '', status: '启用', createdAt: '' })

const filteredUsers = computed(() => {
  return allUsers.value.filter(u => {
    return (
      (!selectedOrg.value || u.department.includes(selectedOrg.value)) &&
      (!searchNickname.value || u.nickname.includes(searchNickname.value)) &&
      (!searchPhone.value || u.phone.includes(searchPhone.value)) &&
      (!searchStatus.value || u.status === searchStatus.value) &&
      (!searchDate.value || u.createdAt.startsWith(searchDate.value))
    )
  })
})
const maxPage = computed(() => Math.max(1, Math.ceil(filteredUsers.value.length / pageSize)))
const pagedUsers = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredUsers.value.slice(start, start + pageSize)
})
function selectOrg(org) {
  selectedOrg.value = org
  page.value = 1
}
function filterUsers() {
  page.value = 1
}
function resetFilters() {
  searchNickname.value = ''
  searchPhone.value = ''
  searchStatus.value = ''
  searchDate.value = ''
  selectedOrg.value = ''
  page.value = 1
}
function closeForm() {
  showAddForm.value = false
  showEditForm.value = false
  form.value = { id: null, nickname: '', username: '', department: '', phone: '', status: '启用', createdAt: '' }
}
function addUser() {
  const newId = allUsers.value.length ? Math.max(...allUsers.value.map(u => u.id)) + 1 : 1
  allUsers.value.push({ ...form.value, id: newId })
  closeForm()
}
function editUser(user) {
  form.value = { ...user }
  showEditForm.value = true
}
function updateUser() {
  const idx = allUsers.value.findIndex(u => u.id === form.value.id)
  if (idx !== -1) allUsers.value[idx] = { ...form.value }
  closeForm()
}
function confirmDelete(user) {
  deleteTarget.value = user
  showDeleteConfirm.value = true
}
function deleteUser() {
  allUsers.value.splice(allUsers.value.findIndex(u => u.id === deleteTarget.value.id), 1)
  showDeleteConfirm.value = false
  deleteTarget.value = null
}
</script> 