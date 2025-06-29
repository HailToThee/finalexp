# 数据库迁移到SQLite

本项目已从PostgreSQL数据库迁移到SQLite数据库。

## 变更内容

### 1. Docker Compose配置 (`docker-compose.yml`)
- 移除了PostgreSQL服务 (`db`)
- 移除了数据库健康检查配置
- 添加了SQLite数据卷 (`sqlite_data`)
- 简化了服务依赖关系

### 2. 数据库配置 (`backend/app/db.py`)
- 将数据库URL从PostgreSQL更改为SQLite
- 添加了SQLite特定的连接参数 (`check_same_thread=False`)
- 自动创建数据目录

### 3. 数据库初始化脚本 (`backend/init_db.py`)
- 更新数据库连接字符串
- 简化了重试逻辑（SQLite启动更快）
- 保持相同的用户创建逻辑

### 4. 依赖管理 (`backend/requirements.txt`)
- 移除了PostgreSQL驱动 (`psycopg2-binary`)
- SQLite是Python内置的，无需额外依赖

### 5. Alembic配置
- 更新了 `alembic.ini` 中的数据库URL
- 修改了 `backend/app/alembic/env.py` 以支持SQLite

## 优势

1. **简化部署**: 无需单独的数据库服务
2. **减少资源消耗**: SQLite是轻量级数据库
3. **易于备份**: 整个数据库就是一个文件
4. **开发友好**: 无需复杂的数据库配置

## 使用方法

### 启动服务
```bash
docker-compose up
```

### 初始化数据库
```bash
docker-compose run init_db_service
```

### 测试数据库配置
```bash
cd backend
python test_sqlite.py
```

## 数据文件位置

SQLite数据库文件位于容器内的 `/app/data/modelsafety.db`，通过Docker卷持久化存储。

## 注意事项

1. SQLite适合中小型应用，如果数据量很大或需要高并发，建议使用PostgreSQL
2. SQLite不支持某些高级数据库功能（如复杂的并发控制）
3. 备份时只需要复制数据库文件即可

## 回滚到PostgreSQL

如果需要回滚到PostgreSQL，可以：
1. 恢复原始的 `docker-compose.yml`
2. 恢复 `backend/app/db.py` 中的PostgreSQL配置
3. 在 `requirements.txt` 中重新添加 `psycopg2-binary`
4. 恢复alembic配置 