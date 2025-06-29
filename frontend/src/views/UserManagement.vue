<template>
  <div class="flex min-h-screen bg-gray-50">
    <!-- 左侧部门树 -->
    <div class="w-64 bg-white shadow-lg rounded-r-2xl p-6 mr-8 mt-8 h-fit">
      <div class="font-bold text-lg mb-4">组织结构</div>
      <ul>
        <li v-for="org in orgTree" :key="org.id" class="mb-2">
          <div class="font-semibold cursor-pointer" @click="selectOrg(org)">{{ org.name }}</div>
          <ul v-if="org.children" class="ml-4 mt-1">
            <li v-for="child in org.children" :key="child.id" class="cursor-pointer hover:text-blue-600" @click.stop="selectOrg(child)">{{ child.name }}</li>
          </ul>
        </li>
      </ul>
    </div>
    <!-- 主内容区 -->
    <div class="flex-1 max-w-6xl mx-auto p-8">
      <div class="bg-white rounded-xl shadow p-8">
        <!-- 顶部筛选栏 -->
        <div class="flex items-center mb-6 space-x-2">
          <input v-model="searchNickname" type="text" placeholder="用户昵称" class="border rounded px-3 py-2 w-40" />
          <input v-model="searchUsername" type="text" placeholder="用户名" class="border rounded px-3 py-2 w-32" />
          <input v-model="searchPhone" type="text" placeholder="手机号" class="border rounded px-3 py-2 w-32" />
          <select v-model="searchStatus" class="border rounded px-3 py-2 w-32">
            <option value="">用户状态</option>
            <option value="启用">启用</option>
            <option value="禁用">禁用</option>
          </select>
          <select v-model="searchDepartment" class="border rounded px-3 py-2 w-32">
            <option value="">全部部门</option>
            <option v-for="d in departmentList" :key="d" :value="d">{{ d }}</option>
          </select>
          <button @click="filterUsers" class="bg-blue-500 text-white px-4 py-2 rounded">查询</button>
          <button @click="resetFilters" class="bg-gray-200 text-gray-700 px-4 py-2 rounded">重置</button>
          <button @click="showAddForm=true" class="bg-green-500 text-white px-4 py-2 rounded">+ 新增</button>
        </div>
        <!-- 用户表格 -->
        <div class="bg-gray-50 rounded-lg shadow-inner p-4">
          <table class="min-w-full text-sm">
            <thead class="bg-gray-100">
              <tr>
                <th class="py-2 px-4 border-b">用户编号</th>
                <th class="py-2 px-4 border-b">用户昵称</th>
                <th class="py-2 px-4 border-b">用户名</th>
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
                  <span :class="user.status==='启用' ? 'text-green-600' : 'text-gray-400'">{{ user.status }}</span>
                </td>
                <td class="py-2 px-4 border-b">{{ user.createdAt }}</td>
                <td class="py-2 px-4 border-b space-x-2">
                  <button class="text-blue-500 hover:underline" @click="editUser(user)">修改</button>
                  <button class="text-red-500 hover:underline" @click="confirmDelete(user)">删除</button>
                  <button class="text-gray-500 hover:underline" @click="showDetail(user)">更多</button>
                </td>
              </tr>
              <tr v-if="pagedUsers.length === 0">
                <td colspan="8" class="text-center py-4 text-gray-400">暂无用户</td>
              </tr>
            </tbody>
          </table>
          <!-- 分页 -->
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
          <div class="bg-white rounded-xl shadow-xl p-8 w-full max-w-2xl relative">
            <button class="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl" @click="closeForm">×</button>
            <h2 class="text-2xl font-bold mb-6 text-center">{{ showAddForm ? '新增用户' : '编辑用户' }}</h2>
            <form @submit.prevent="showAddForm ? addUserData() : updateUserData()">
              <div class="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label class="block text-gray-600 mb-1">用户昵称</label>
                  <input v-model="form.nickname" type="text" class="w-full px-3 py-2 border rounded" required />
                </div>
                <div>
                  <label class="block text-gray-600 mb-1">用户名</label>
                  <input v-model="form.username" type="text" class="w-full px-3 py-2 border rounded" required />
                </div>
                <div>
                  <label class="block text-gray-600 mb-1">用户密码</label>
                  <input v-model="form.password" type="password" class="w-full px-3 py-2 border rounded" :required="showAddForm" />
                </div>
                <div>
                  <label class="block text-gray-600 mb-1">手机号</label>
                  <input v-model="form.phone" type="text" class="w-full px-3 py-2 border rounded" />
                </div>
                <div>
                  <label class="block text-gray-600 mb-1">部门</label>
                  <select v-model="form.department" class="w-full px-3 py-2 border rounded">
                    <option value="">请选择部门</option>
                    <option v-for="d in departmentList" :key="d" :value="d">{{ d }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-gray-600 mb-1">岗位</label>
                  <input v-model="form.position" type="text" class="w-full px-3 py-2 border rounded" />
                </div>
                <div>
                  <label class="block text-gray-600 mb-1">邮箱</label>
                  <input v-model="form.email" type="email" class="w-full px-3 py-2 border rounded" />
                </div>
                <div>
                  <label class="block text-gray-600 mb-1">用户性别</label>
                  <select v-model="form.gender" class="w-full px-3 py-2 border rounded">
                    <option value="">请选择</option>
                    <option value="男">男</option>
                    <option value="女">女</option>
                  </select>
                </div>
              </div>
              <div class="mb-4">
                <label class="block text-gray-600 mb-1">备注</label>
                <textarea v-model="form.remark" class="w-full px-3 py-2 border rounded" maxlength="512" placeholder="请输入内容" />
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
              <button class="px-6 py-2 rounded bg-red-600 text-white hover:bg-red-700" @click="deleteUserConfirm">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchUsers, addUser, updateUser, deleteUser } from '@/api.js'
// 组织树静态示例
const orgTree = ref([
  { id: 1, name: '武汉总部', children: [
    { id: 2, name: '武汉总部' },
    { id: 3, name: '长沙分点' },
    { id: 4, name: '市场部门' },
    { id: 5, name: '财务部门' },
  ]},
  { id: 6, name: '新部门', children: [
    { id: 7, name: '测试部门' },
    { id: 8, name: '测试部门2' },
  ]}
])
const selectedOrg = ref(null)
const allUsers = ref([])
const searchNickname = ref('')
const searchUsername = ref('')
const searchPhone = ref('')
const searchStatus = ref('')
const searchDepartment = ref('')
const page = ref(1)
const pageSize = 10
const showAddForm = ref(false)
const showEditForm = ref(false)
const showDeleteConfirm = ref(false)
const deleteTarget = ref(null)
const form = ref({ id: null, nickname: '', username: '', password: '', phone: '', department: '', position: '', email: '', gender: '', remark: '', status: '启用' })
const departmentList = ['武汉总部','长沙分点','市场部门','财务部门','测试部门','测试部门2']
// 获取用户列表
async function fetchUsersData() {
  try {
    const res = await fetchUsers()
    allUsers.value = res.data.users || []
  } catch (e) {
    allUsers.value = []
  }
}
onMounted(() => {
  fetchUsersData()
})
const filteredUsers = computed(() => {
  return allUsers.value.filter(u => {
    return (
      (!searchNickname.value || u.nickname.includes(searchNickname.value)) &&
      (!searchUsername.value || u.username.includes(searchUsername.value)) &&
      (!searchPhone.value || u.phone.includes(searchPhone.value)) &&
      (!searchStatus.value || u.status === searchStatus.value) &&
      (!searchDepartment.value || u.department === searchDepartment.value) &&
      (!selectedOrg.value || u.department === selectedOrg.value.name)
    )
  })
})
const maxPage = computed(() => Math.max(1, Math.ceil(filteredUsers.value.length / pageSize)))
const pagedUsers = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredUsers.value.slice(start, start + pageSize)
})
function filterUsers() {
  page.value = 1
}
function resetFilters() {
  searchNickname.value = ''
  searchUsername.value = ''
  searchPhone.value = ''
  searchStatus.value = ''
  searchDepartment.value = ''
  page.value = 1
}
function selectOrg(org) {
  selectedOrg.value = org
  page.value = 1
}
function closeForm() {
  showAddForm.value = false
  showEditForm.value = false
  form.value = { id: null, nickname: '', username: '', password: '', phone: '', department: '', position: '', email: '', gender: '', remark: '', status: '启用' }
}
async function addUserData() {
  try {
    await addUser(form.value)
    closeForm()
    await fetchUsersData()
    alert('用户创建成功')
  } catch (err) {
    alert('用户创建失败')
  }
}
async function updateUserData() {
  try {
    await updateUser(form.value.id, form.value)
    closeForm()
    await fetchUsersData()
    alert('用户更新成功')
  } catch (err) {
    alert('用户更新失败')
  }
}
function editUser(user) {
  form.value = { ...user, password: '' }
  showEditForm.value = true
}
function showDetail(user) {
  alert('用户详情：' + user.nickname)
}
function confirmDelete(user) {
  deleteTarget.value = user
  showDeleteConfirm.value = true
}
async function deleteUserConfirm() {
  try {
    await deleteUser(deleteTarget.value.id)
    showDeleteConfirm.value = false
    await fetchUsersData()
    alert('用户删除成功')
  } catch (err) {
    alert('用户删除失败')
  }
}
</script> 