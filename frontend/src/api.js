import axios from 'axios'

// ========== 用户管理 ==========
export function fetchUsers() {
  return axios.get('/api/user/list')
}
export function addUser(data) {
  return axios.post('/api/user/create', data)
}
export function updateUser(id, data) {
  return axios.put(`/api/user/${id}`, data)
}
export function deleteUser(id) {
  return axios.delete(`/api/user/${id}`)
}

// ========== 认证 ==========
export function login(data) {
  const params = new URLSearchParams();
  params.append('username', data.username);
  params.append('password', data.password);
  return axios.post('/api/auth/token', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
}

// ========== 样本库与扩增分析 ==========
export function uploadSample(formData) {
  return axios.post('/api/sample/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export function deleteSample(id) {
  return axios.delete(`/api/sample/${id}`)
}
export function getSampleInfo(id) {
  return axios.get(`/api/sample/info/${id}`)
}

// ========== 算法管理与调试 ==========
export function uploadAlgorithm(formData) {
  return axios.post('/api/algorithm/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export function deleteAlgorithm(id) {
  return axios.delete(`/api/algorithm/${id}`)
}
export function getAlgorithmInfo(id) {
  return axios.get(`/api/algorithm/info/${id}`)
}
export function getDebugLogs(id) {
  return axios.get(`/api/algorithm/debug/logs/${id}`)
}
export function runDebug(data) {
  return axios.post('/api/algorithm/debug', data)
}

// ========== 算法/模型目录结构与文件操作 ==========
export function getAlgorithmTree(id) {
  return axios.get(`/api/algorithm/${id}/tree`)
}
export function uploadAlgorithmFile(id, formData) {
  return axios.post(`/api/algorithm/${id}/file`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export function createAlgorithmFolder(id, data) {
  return axios.post(`/api/algorithm/${id}/folder`, data)
}
export function deleteAlgorithmFile(id, path) {
  return axios.delete(`/api/algorithm/${id}/file`, { params: { path } })
}
export function renameAlgorithmFile(id, data) {
  return axios.put(`/api/algorithm/${id}/file`, data)
}
export function getAlgorithmFileContent(id, path) {
  return axios.get(`/api/algorithm/${id}/file`, { params: { path } })
}
export function saveAlgorithmFileContent(id, path, content) {
  return axios.put(`/api/algorithm/${id}/file`, { path, content })
}

// ========== 模型管理与评估/预测 ==========
export function fetchModels() {
  return axios.get('/api/model/list')
}
export function uploadModel(formData) {
  return axios.post('/api/model/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export function deleteModel(id) {
  return axios.delete(`/api/model/${id}`)
}
export function downloadModel(id) {
  return axios.get(`/api/file/download/${id}`, { responseType: 'blob' })
}

// ========== 模型评估/预测任务流 ==========
export function createModelEvalTask(data) {
  return axios.post('/api/model/evaluate', data)
}
export function createModelPredictTask(data) {
  return axios.post('/api/model/predict', data)
}
export function getModelTaskList(params) {
  return axios.get('/api/model/task_list', { params })
}
export function getModelTaskDetail(taskId) {
  return axios.get(`/api/model/task/${taskId}`)
}

// ========== 模型导出ONNX ==========
export function exportModelOnnx(modelId) {
  return axios.post(`/api/model/export_onnx`, { id: modelId }, { responseType: 'blob' })
}

// ========== 模型下载 ==========
export function downloadModelFile(fileId) {
  return axios.get(`/api/file/download/${fileId}`, { responseType: 'blob' })
}

// ========== 模型目录结构/文件操作 ==========
export function getModelTree(id) {
  return axios.get(`/api/model/${id}/tree`)
}
export function uploadModelFile(id, formData) {
  return axios.post(`/api/model/${id}/file`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export function createModelFolder(id, data) {
  return axios.post(`/api/model/${id}/folder`, data)
}
export function deleteModelFile(id, path) {
  return axios.delete(`/api/model/${id}/file`, { params: { path } })
}
export function renameModelFile(id, data) {
  return axios.put(`/api/model/${id}/file`, data)
}
export function getModelFileContent(id, path) {
  return axios.get(`/api/model/${id}/file`, { params: { path } })
}
export function saveModelFileContent(id, path, content) {
  return axios.put(`/api/model/${id}/file`, { path, content })
}

// ========== 推理服务 ==========
export function fetchServices() {
  return axios.get('/api/inference/list')
}
export function addService(data) {
  return axios.post('/api/inference/deploy', data)
}
export function deleteService(id) {
  return axios.delete(`/api/inference/${id}`)
}
export function getInferenceResult(id) {
  return axios.get(`/api/inference/result/${id}`)
}

// ========== 资源管理 ==========
export function fetchOrgs() {
  return axios.get('/api/org/list')
}
export function createOrg(data) {
  return axios.post('/api/org/create', data)
}
export function setQuota(data) {
  return axios.post('/api/org/quota', data)
}
export function releaseResource(data) {
  return axios.post('/api/org/release', data)
}

// ========== 镜像管理 ==========
export function fetchImages(params) {
  return axios.get('/api/image/list', { params })
}
export function uploadImage(formData) {
  return axios.post('/api/image/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export function deleteImage(id) {
  return axios.delete(`/api/image/${id}`)
}
export function getImageDetail(id) {
  return axios.get(`/api/image/detail/${id}`)
}
export function pushImage(data) {
  return axios.post('/api/image/push', data)
}
export function getPushHistory() {
  return axios.get('/api/image/push/history')
}
export function getPushStatus() {
  return axios.get('/api/image/push/status')
}
export function fetchRepos() {
  return axios.get('/api/image/repo/list')
}
export function createRepo(data) {
  const formData = new FormData();
  formData.append('name', data.name);
  formData.append('type', data.type);
  if (data.description) formData.append('description', data.description);
  return axios.post('/api/image/repo/create', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
}
export function updatePermission(data) {
  const formData = new FormData();
  formData.append('id', data.id);
  formData.append('permission', data.permission);
  return axios.post('/api/image/permission', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
}
export function downloadImage(id) {
  return axios.get(`/api/image/download/${id}`, { responseType: 'blob' })
}

// ========== 文件管理 ==========
export function fetchFiles() {
  return axios.get('/api/file/list')
}
export function uploadFile(formData) {
  return axios.post('/api/file/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export function uploadFolder(formData) {
  return axios.post('/api/file/upload_folder', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export function deleteFile(id) {
  return axios.delete(`/api/file/${id}`)
}
export function downloadFile(id) {
  return axios.get(`/api/file/download/${id}`, { responseType: 'blob' })
}
export function renameFile(id, newName) {
  const formData = new FormData();
  formData.append('new_name', newName);
  return axios.put(`/api/file/${id}/rename`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
}
export function moveFile(id, folderId) {
  const formData = new FormData();
  if (folderId) formData.append('folder_id', folderId);
  return axios.put(`/api/file/move/${id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
}
export function decompressFile(id) {
  return axios.post(`/api/file/decompress/${id}`)
}
export function batchDecompress(fileIds) {
  return axios.post('/api/file/batch_decompress', fileIds)
}
export function uploadChunk(formData) {
  return axios.post('/api/file/upload_chunk', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export function batchDelete(data) {
  return axios.post('/api/file/batch_delete', data)
}
export function batchDeleteMixed(fileIds, folderIds) {
  const formData = new FormData();
  fileIds.forEach(id => formData.append('file_ids', id));
  folderIds.forEach(id => formData.append('folder_ids', id));
  return axios.post('/api/file/batch_delete_mixed', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
}
export function batchDownload(data) {
  return axios.post('/api/file/batch_download', data, { responseType: 'blob' })
}
export function batchDownloadMixed(fileIds, folderIds) {
  const formData = new FormData();
  fileIds.forEach(id => formData.append('file_ids', id));
  folderIds.forEach(id => formData.append('folder_ids', id));
  return axios.post('/api/file/batch_download_mixed', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    responseType: 'blob'
  });
}

// ========== 文件夹管理 ==========
export function fetchFolders(parentId = null) {
  const params = parentId ? { parent_id: parentId } : {};
  return axios.get('/api/file/folders', { params });
}
export function createFolder(name, parentId = null, description = '') {
  const formData = new FormData();
  formData.append('name', name);
  if (parentId) formData.append('parent_id', parentId);
  if (description) formData.append('description', description);
  return axios.post('/api/file/folders', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
}
export function deleteFolder(folderId) {
  return axios.delete(`/api/file/folders/${folderId}`);
}
export function renameFolder(folderId, newName) {
  const formData = new FormData();
  formData.append('new_name', newName);
  return axios.put(`/api/file/folders/${folderId}/rename`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
}
export function getFileTree() {
  return axios.get('/api/file/tree');
}

// ========== 算法列表 ==========
export function fetchAlgorithms() {
  return axios.get('/api/algorithm/list')
}

// ========== 样本列表 ==========
export function fetchSamples() {
  return axios.get('/api/sample/list')
}

// ========== 样本分布/详情 ==========
export function fetchSampleInfo(id) {
  if (id) {
    return axios.get(`/api/sample/${id}/info`)
  } else {
    return axios.get('/api/sample/distribution')
  }
}

// ========== 对抗样本生成模块 ==========

// 获取对抗样本任务列表
export function fetchAdversarialTasks() {
  return axios.get('/api/adversarial/tasks')
}

// 创建对抗样本任务
export function createAdversarialTask(data) {
  return axios.post('/api/adversarial/tasks', data)
}

// 更新对抗样本任务
export function updateAdversarialTask(id, data) {
  return axios.put(`/api/adversarial/tasks/${id}`, data)
}

// 删除对抗样本任务
export function deleteAdversarialTask(id) {
  return axios.delete(`/api/adversarial/tasks/${id}`)
}

// 获取任务详情
export function getAdversarialTaskDetail(id) {
  return axios.get(`/api/adversarial/tasks/${id}`)
}

// 获取可用算法列表
export function fetchAvailableAlgorithms() {
  return axios.get('/api/adversarial/algorithms')
}

// 获取可用模型列表
export function fetchAvailableModels() {
  return axios.get('/api/adversarial/models')
}

// 获取可用数据集列表
export function fetchAvailableDatasets() {
  return axios.get('/api/adversarial/datasets')
}

// 保存超参数配置
export function saveHyperParams(taskId, hyperParams) {
  return axios.post(`/api/adversarial/tasks/${taskId}/hyperparams`, hyperParams)
}

// 开始超参数调优
export function startHyperParamTuning(taskId, hyperParams) {
  return axios.post(`/api/adversarial/tasks/${taskId}/tuning`, hyperParams)
}

// 保存训练配置
export function saveTrainingConfig(taskId, trainingConfig) {
  return axios.post(`/api/adversarial/tasks/${taskId}/training`, trainingConfig)
}

// 开始训练
export function startTraining(taskId, trainingConfig) {
  return axios.post(`/api/adversarial/tasks/${taskId}/train`, trainingConfig)
}

// 获取任务监控数据
export function getTaskMonitoring(taskId) {
  return axios.get(`/api/adversarial/tasks/${taskId}/monitoring`)
}

// 停止任务
export function stopTask(taskId) {
  return axios.post(`/api/adversarial/tasks/${taskId}/stop`)
}

// 暂停任务
export function pauseTask(taskId) {
  return axios.post(`/api/adversarial/tasks/${taskId}/pause`)
}

// 恢复任务
export function resumeTask(taskId) {
  return axios.post(`/api/adversarial/tasks/${taskId}/resume`)
}

// 获取任务日志
export function getTaskLogs(taskId) {
  return axios.get(`/api/adversarial/tasks/${taskId}/logs`)
}

// 下载生成的对抗样本
export function downloadAdversarialSamples(taskId) {
  return axios.get(`/api/adversarial/tasks/${taskId}/download`, { responseType: 'blob' })
}

// 获取任务结果
export function getTaskResults(taskId) {
  return axios.get(`/api/adversarial/tasks/${taskId}/results`)
}

// 导出任务报告
export function exportTaskReport(taskId) {
  return axios.get(`/api/adversarial/tasks/${taskId}/report`, { responseType: 'blob' })
}

// 批量操作任务
export function batchOperationTask(taskIds, operation) {
  return axios.post('/api/adversarial/tasks/batch', { taskIds, operation })
}

// 获取超参数调优历史
export function getHyperParamHistory(taskId) {
  return axios.get(`/api/adversarial/tasks/${taskId}/tuning/history`)
}

// 获取训练历史
export function getTrainingHistory(taskId) {
  return axios.get(`/api/adversarial/tasks/${taskId}/training/history`)
}

// 克隆任务
export function cloneTask(taskId) {
  return axios.post(`/api/adversarial/tasks/${taskId}/clone`)
}

// 获取任务统计信息
export function getTaskStatistics() {
  return axios.get('/api/adversarial/tasks/statistics')
} 