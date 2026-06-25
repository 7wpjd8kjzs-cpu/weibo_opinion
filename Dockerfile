FROM python:3.10-slim

# 安装中文字体和依赖
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    fontconfig \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . /app
WORKDIR /app

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 运行 Streamlit
CMD ["streamlit", "run", "app.py"]
