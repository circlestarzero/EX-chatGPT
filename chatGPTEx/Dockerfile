# FROM python:slim or python:alpine 以精简镜像，但需要额外下载依赖
FROM python:3.11.2
LABEL Maintainer="https://github.com/acdiost" Desc="EXChatGPT Docker"

COPY requirements.txt .

# 使用清华源以提高下载速度
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 使用非 root 用户运行以降低权限
USER www-data

WORKDIR /app/

COPY --chown=www-data:www-data . .

EXPOSE 5000

ENTRYPOINT ["python", "main.py"]
