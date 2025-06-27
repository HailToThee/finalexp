<template>
    <div class="min-h-screen bg-gray-50 flex flex-col items-center pt-12">
        <div class="w-full max-w-4xl">
            <div class="bg-gradient-to-r from-blue-700 to-blue-500 rounded-2xl shadow-xl p-10 mb-12 flex flex-col items-center">
                <div class="flex items-center mb-4">
                    <span class="text-4xl mr-4 text-white">🧬</span>
                    <h1 class="text-3xl font-extrabold text-white tracking-widest">AI模型安全评估平台</h1>
                </div>
                <p class="text-lg text-blue-100 mb-2 text-center leading-relaxed">支持AI模型上传、对抗样本生成与安全性评估，助力AI安全研究与应用。</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-10">
                <router-link to="/users" class="block rounded-xl shadow-lg p-8 bg-gradient-to-br from-cyan-100 to-blue-100 hover:from-cyan-200 hover:to-blue-200 transition transform hover:-translate-y-1">
                    <div class="text-xl font-bold mb-2 text-cyan-700">用户管理</div>
                    <div class="text-gray-600">组织、用户的分组与权限管理</div>
                </router-link>
                <router-link to="/models" class="block rounded-xl shadow-lg p-8 bg-gradient-to-br from-blue-100 to-blue-200 hover:from-blue-200 hover:to-blue-300 transition transform hover:-translate-y-1">
                    <div class="text-xl font-bold mb-2 text-blue-800">模型管理</div>
                    <div class="text-gray-600">上传、管理和评估AI模型</div>
                </router-link>
                <router-link to="/file" class="block rounded-xl shadow-lg p-8 bg-gradient-to-br from-purple-100 to-blue-100 hover:from-purple-200 hover:to-blue-200 transition transform hover:-translate-y-1">
                    <div class="text-xl font-bold mb-2 text-purple-800">文件管理</div>
                    <div class="text-gray-600">上传、管理数据集和文件</div>
                </router-link>
                <router-link to="/algorithms" class="block rounded-xl shadow-lg p-8 bg-gradient-to-br from-green-100 to-blue-100 hover:from-green-200 hover:to-blue-200 transition transform hover:-translate-y-1">
                    <div class="text-xl font-bold mb-2 text-green-800">算法管理</div>
                    <div class="text-gray-600">管理对抗样本生成算法</div>
                </router-link>
                <router-link to="/samples" class="block rounded-xl shadow-lg p-8 bg-gradient-to-br from-yellow-100 to-blue-100 hover:from-yellow-200 hover:to-blue-200 transition transform hover:-translate-y-1">
                    <div class="text-xl font-bold mb-2 text-yellow-700">样本库</div>
                    <div class="text-gray-600">管理和增强样本集</div>
                </router-link>
                <router-link to="/inference" class="block rounded-xl shadow-lg p-8 bg-gradient-to-br from-pink-100 to-blue-100 hover:from-pink-200 hover:to-blue-200 transition transform hover:-translate-y-1">
                    <div class="text-xl font-bold mb-2 text-pink-700">推理服务</div>
                    <div class="text-gray-600">模型部署与在线推理</div>
                </router-link>
            </div>
        </div>
    </div>
</template>

<script setup>
// 无需js逻辑
</script>