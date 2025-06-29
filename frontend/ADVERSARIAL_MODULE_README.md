# 对抗样本生成模块说明文档

## 概述

对抗样本生成模块是AI模型安全评估平台的核心功能之一，提供了完整的对抗样本生成、超参数调优和算法训练功能。该模块帮助研究人员和开发者评估AI模型的安全性，发现模型的潜在漏洞。

## 功能特性

### 1. 任务管理
- **任务创建**：支持创建新的对抗样本生成任务
- **任务列表**：查看所有对抗样本生成任务
- **任务状态**：实时监控任务运行状态（待运行、运行中、已完成、失败、暂停）
- **任务操作**：支持编辑、删除、克隆任务

### 2. 超参数调优
- **搜索空间配置**：支持连续、离散、分类三种参数类型
- **优化算法**：提供随机搜索、贝叶斯优化、网格搜索、遗传算法、TPE等多种优化策略
- **实时监控**：显示调优进度、最佳得分、试验结果
- **可视化**：得分变化趋势图和参数重要性分析

### 3. 算法训练
- **训练参数配置**：学习率、批次大小、训练轮数、优化器等
- **高级配置**：数据增强、混合精度、分布式训练、模型检查点等
- **实时监控**：训练进度、损失曲线、准确率曲线
- **日志管理**：实时训练日志，支持导出和清空

### 4. 结果分析
- **性能指标**：准确率、精确率、召回率、F1分数
- **对抗性能**：攻击成功率、平均扰动、鲁棒性
- **资源使用**：GPU使用率、内存使用、训练时间
- **报告导出**：支持生成详细的任务报告

## 文件结构

```
src/views/
├── AdversarialGeneration.vue    # 主页面 - 任务管理
├── HyperParamTuning.vue         # 超参数调优页面
└── AlgorithmTraining.vue        # 算法训练页面

src/api.js                       # API接口定义（新增25个接口）
src/router/index.js              # 路由配置（新增3个路由）
src/App.vue                      # 主应用（新增导航菜单项）
```

## 页面说明

### 1. 对抗样本生成主页面 (`/adversarial`)
- **左侧**：任务管理面板，显示所有对抗样本生成任务
- **右侧**：任务详情和配置面板
  - 任务基本信息
  - 超参数配置
  - 训练配置
  - 实时监控

### 2. 超参数调优页面 (`/adversarial/tuning/:taskId`)
- **左侧**：搜索空间配置和调优策略配置
- **右侧**：调优进度、试验结果、最佳参数展示
- **底部**：可视化图表区域

### 3. 算法训练页面 (`/adversarial/training/:taskId`)
- **左侧**：训练参数配置和高级配置
- **右侧**：训练进度、训练曲线、训练日志
- **底部**：模型评估结果

## API接口

### 任务管理接口
- `GET /api/adversarial/tasks` - 获取任务列表
- `POST /api/adversarial/tasks` - 创建任务
- `PUT /api/adversarial/tasks/{id}` - 更新任务
- `DELETE /api/adversarial/tasks/{id}` - 删除任务
- `GET /api/adversarial/tasks/{id}` - 获取任务详情

### 资源配置接口
- `GET /api/adversarial/algorithms` - 获取可用算法
- `GET /api/adversarial/models` - 获取可用模型
- `GET /api/adversarial/datasets` - 获取可用数据集

### 超参数调优接口
- `POST /api/adversarial/tasks/{id}/hyperparams` - 保存超参数配置
- `POST /api/adversarial/tasks/{id}/tuning` - 开始超参数调优
- `GET /api/adversarial/tasks/{id}/tuning/history` - 获取调优历史

### 算法训练接口
- `POST /api/adversarial/tasks/{id}/training` - 保存训练配置
- `POST /api/adversarial/tasks/{id}/train` - 开始训练
- `GET /api/adversarial/tasks/{id}/training/history` - 获取训练历史

### 监控和控制接口
- `GET /api/adversarial/tasks/{id}/monitoring` - 获取监控数据
- `POST /api/adversarial/tasks/{id}/stop` - 停止任务
- `POST /api/adversarial/tasks/{id}/pause` - 暂停任务
- `POST /api/adversarial/tasks/{id}/resume` - 恢复任务
- `GET /api/adversarial/tasks/{id}/logs` - 获取任务日志

### 结果和导出接口
- `GET /api/adversarial/tasks/{id}/results` - 获取任务结果
- `GET /api/adversarial/tasks/{id}/download` - 下载对抗样本
- `GET /api/adversarial/tasks/{id}/report` - 导出任务报告
- `POST /api/adversarial/tasks/batch` - 批量操作任务
- `POST /api/adversarial/tasks/{id}/clone` - 克隆任务
- `GET /api/adversarial/tasks/statistics` - 获取统计信息

## 使用流程

### 1. 创建对抗样本任务
1. 进入对抗样本生成页面
2. 点击"新建对抗样本任务"
3. 填写任务名称、描述
4. 选择算法、目标模型、数据集
5. 点击"创建任务"

### 2. 配置超参数
1. 选择任务，进入任务详情
2. 在超参数配置区域设置参数
3. 点击"保存配置"
4. 点击"开始超参数调优"

### 3. 配置训练参数
1. 在训练配置区域设置训练参数
2. 配置高级选项（数据增强、混合精度等）
3. 点击"保存配置"
4. 点击"开始训练"

### 4. 监控和结果
1. 在实时监控区域查看进度
2. 查看训练日志和曲线
3. 分析评估结果
4. 下载生成的对抗样本或导出报告

## 技术特点

### 1. 响应式设计
- 使用Vue 3 Composition API
- 响应式布局，支持不同屏幕尺寸
- 实时数据更新

### 2. 用户体验
- 直观的界面设计
- 实时进度显示
- 丰富的交互反馈
- 详细的状态提示

### 3. 功能完整性
- 完整的任务生命周期管理
- 多种优化算法支持
- 详细的监控和分析
- 灵活的配置选项

### 4. 扩展性
- 模块化设计
- 清晰的API接口
- 易于添加新功能
- 支持自定义配置

## 注意事项

1. **权限控制**：所有接口都需要用户登录认证
2. **数据格式**：上传文件使用multipart/form-data格式
3. **实时更新**：监控数据每2-5秒自动更新
4. **错误处理**：完善的错误提示和异常处理
5. **资源管理**：支持任务暂停、恢复、停止操作

## 后续扩展

1. **更多算法**：支持更多对抗攻击算法
2. **可视化增强**：添加更多图表和可视化功能
3. **批量操作**：支持批量任务管理
4. **报告模板**：提供多种报告模板
5. **集成测试**：与现有模块深度集成 