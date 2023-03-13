# FROM python:slim or python:alpine 以精简镜像，但需要额外下载依赖
FROM python:3.11.2
LABEL Maintainer="https://github.com/acdiost" Desc="EXChatGPT Docker"

COPY requirements.txt .

# 使用清华源以提高下载速度
RUN pip install --no-cache-dir -r https://raw.githubusercontent.com/circlestarzero/EX-chatGPT/main/chatGPTEx/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

ENV LANG="C.UTF-8" \
    TZ="Asia/Shanghai" \
    REPO_URL="https://ghproxy.com/https://github.com/onlyLTY/EX-chatGPT.git" \
    WORKDIR="/app"
# 使用非 root 用户运行以降低权限
USER www-data

WORKDIR ${WORKDIR}

RUN git clone -b main ${REPO_URL} ${WORKDIR} --depth=1 --recurse-submodule \
    && chmod +x ${WORKDIR}/chatGPTEx/entrypoint.sh \
    && chown -R www-data:www-data ${WORKDIR}

EXPOSE 5000

ENTRYPOINT ["/app/chatGPTEx/entrypoint.sh"]
