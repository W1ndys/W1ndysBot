# 使用官方的 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制app目录下的所有文件到容器中
COPY app /app

# 安装依赖
RUN pip install -r requirements.txt

# 启动应用
CMD ["python", "main.py"]

