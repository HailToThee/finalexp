FROM python:3.9-slim

WORKDIR /app

# 1. 设置 APT 镜像源（解决之前的问题，如果已解决可忽略此步骤或根据需要调整）
#    确保 /etc/apt/sources.list 存在并替换为中科大源
RUN test -f /etc/apt/sources.list || touch /etc/apt/sources.list && \
    printf "deb https://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free\ndeb https://mirrors.ustc.edu.cn/debian-security/ bookworm-security main contrib non-free\ndeb https://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free\n" | tee /etc/apt/sources.list

# 2. 安装必要的系统级构建工具
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libopenblas-dev \
    liblapack-dev && \
    rm -rf /var/lib/apt/lists/*

# --- START OF PIP SOURCE MODIFICATION ---
# 3. 设置 Pip 镜像源为中科大源
ENV PIP_INDEX_URL=https://pypi.mirrors.ustc.edu.cn/simple/
ENV PIP_TRUSTED_HOST=pypi.mirrors.ustc.edu.cn
# --- END OF PIP SOURCE MODIFICATION ---

# 4. 优先复制 requirements.txt 文件以利用缓存
COPY ./requirements.txt .

# 5. 安装 Python 依赖
#    因为上面设置了环境变量，这里不需要再加 -i 参数
RUN pip install -r requirements.txt

# 6. 最后再复制应用程序代码
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

