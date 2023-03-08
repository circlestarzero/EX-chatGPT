FROM python:latest # slim or alpine
LABEL Maintainer="https://github.com/acdiost" Desc="EXChatGPT Docker"

WORKDIR /app/

COPY . /app/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt # -i https://pypi.tuna.tsinghua.edu.cn/simple/

EXPOSE 5000

ENTRYPOINT ["python", "main.py"]
