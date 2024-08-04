# 使用官方的 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到工作目录
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露应用运行的端口（假设应用运行在3001端口）
EXPOSE 3001

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 运行应用
CMD ["python", "app/main.py"]