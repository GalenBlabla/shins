# 使用 Python 官方镜像作为基础镜像
FROM python:3.10

# 将 /usr/src 设置为工作目录
WORKDIR /usr/src

# 复制 requirements.txt 并安装依赖
COPY requirements.txt ./
RUN pip install -r requirements.txt

# 复制项目文件到容器内
COPY . ./app

# 指定启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
