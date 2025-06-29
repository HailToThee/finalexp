# 项目手工启动指南

本文档介绍如何在不使用Docker的情况下手工启动AI模型安全性评估平台。

## 系统要求

### 基础要求
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 推荐配置
- 内存: 8GB+
- 存储: 20GB+ (用于AI模型和依赖)
- GPU: 可选，用于加速深度学习模型

## 环境准备

### 1. 克隆项目
```bash
git clone <项目地址>
cd FINAL_EXP
```

### 2. 创建Python虚拟环境
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

### 3. 安装Python依赖
```bash
# 确保在虚拟环境中
pip install --upgrade pip
pip install -r requirements.txt
```

**注意**: 由于项目包含大量AI/ML依赖，安装可能需要较长时间。建议：
- 使用国内镜像源加速: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`
- 如果只需要基础功能，可以先安装核心依赖:
```bash
pip install fastapi uvicorn sqlalchemy python-jose passlib python-multipart pydantic python-dotenv
```

### 4. 安装Node.js依赖
```bash
# 进入前端目录
cd ../frontend

# 安装依赖
npm install
# 或使用yarn
# yarn install
```

## 数据库初始化

### 1. 初始化SQLite数据库
```bash
# 回到后端目录
cd ../backend

# 确保虚拟环境已激活
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 运行数据库初始化脚本
python init_db.py
```

成功后会看到类似输出：
```
✅ 数据库初始化完成！
默认用户:
  管理员: admin / admin123
  普通用户: user / user123
```

### 2. 验证数据库配置
```bash
# 测试SQLite配置
python test_sqlite.py
```

## 启动服务

### 1. 启动后端服务

#### 方法一：直接启动
```bash
# 在backend目录下，确保虚拟环境已激活
cd backend
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 启动FastAPI服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 方法二：使用Python模块启动
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 方法三：后台运行（Linux/Mac）
```bash
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
```

### 2. 启动前端服务

#### 方法一：开发模式
```bash
# 进入前端目录
cd frontend

# 启动开发服务器
npm run dev
# 或
yarn dev
```

#### 方法二：生产模式
```bash
# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 访问应用

### 服务地址
- **前端**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

### 默认登录信息
- **管理员账号**: admin / admin123
- **普通用户账号**: user / user123

## 常见问题解决

### 1. 端口冲突
如果8000或5173端口被占用，可以修改端口：

**后端端口修改**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**前端端口修改**:
```bash
# 在frontend目录下创建vite.config.js或修改现有配置
npm run dev -- --port 5174
```

### 2. 数据库权限问题
如果遇到数据库权限错误：
```bash
# 检查数据目录权限
ls -la backend/data/

# 修改权限
chmod 755 backend/data/
chmod 644 backend/data/modelsafety.db
```

### 3. 依赖安装失败
如果某些AI/ML依赖安装失败：

**跳过可选依赖**:
```bash
# 只安装核心依赖
pip install fastapi uvicorn sqlalchemy python-jose passlib python-multipart pydantic python-dotenv
```

**使用conda安装**:
```bash
# 对于PyTorch等大型依赖，建议使用conda
conda install pytorch torchvision -c pytorch
```

### 4. 内存不足
如果系统内存不足，可以：
- 关闭不必要的服务
- 使用更轻量的依赖版本
- 增加系统虚拟内存

## 开发模式配置

### 1. 环境变量配置
创建 `.env` 文件（可选）:
```bash
# backend/.env
DATABASE_URL=sqlite:///./data/modelsafety.db
SECRET_KEY=your-secret-key
DEBUG=True
```

### 2. 热重载配置
后端已配置热重载（`--reload`），前端Vite默认支持热重载。

### 3. 日志配置
查看后端日志：
```bash
# 如果使用nohup启动
tail -f backend.log

# 或者直接在控制台查看
```

## 停止服务

### 1. 停止后端服务
```bash
# 如果在前台运行，按 Ctrl+C
# 如果在后台运行
ps aux | grep uvicorn
kill <进程ID>
```

### 2. 停止前端服务
```bash
# 在控制台按 Ctrl+C
```

### 3. 停止虚拟环境
```bash
deactivate
```

## 生产环境部署

### 1. 使用Gunicorn（推荐）
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2. 使用Nginx反向代理
配置Nginx将请求转发到后端服务。

### 3. 使用PM2管理Node.js进程
```bash
npm install -g pm2
pm2 start npm --name "frontend" -- run dev
```

## 故障排除

### 1. 检查服务状态
```bash
# 检查端口占用
netstat -tulpn | grep :8000
netstat -tulpn | grep :5173

# 检查进程
ps aux | grep uvicorn
ps aux | grep node
```

### 2. 查看日志
```bash
# 后端日志
tail -f backend.log

# 前端日志（在控制台查看）
```

### 3. 重置数据库
```bash
# 删除数据库文件
rm backend/data/modelsafety.db

# 重新初始化
python init_db.py
```

## 性能优化建议

1. **使用SSD存储**：提高数据库和文件I/O性能
2. **配置足够内存**：AI模型需要大量内存
3. **使用GPU加速**：如果支持CUDA，安装GPU版本的PyTorch/TensorFlow
4. **启用缓存**：考虑使用Redis等缓存服务
5. **数据库优化**：定期清理和优化SQLite数据库

## 联系支持

如果遇到问题，请：
1. 检查本文档的故障排除部分
2. 查看项目日志
3. 确认系统环境满足要求
4. 联系项目维护团队 