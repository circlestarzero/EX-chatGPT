# FROM python:slim or python:alpine 以精简镜像，但需要额外下载依赖
FROM python:3.11.2

# 使用清华源以提高下载速度
RUN pip install --no-cache-dir -r https://raw.githubusercontent.com/circlestarzero/EX-chatGPT/main/chatGPTEx/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

ENV LANG="C.UTF-8" \
    TZ="Asia/Shanghai" \
    REPO_URL="https://ghproxy.com/https://github.com/circlestarzero/EX-chatGPT.git" \
    WORKDIR="/app" \
    AUTO_UPDATE="true"

WORKDIR ${WORKDIR}

RUN git clone -b main ${REPO_URL} ${WORKDIR} --depth=1 --recurse-submodule \
    && chmod +x ${WORKDIR}/chatGPTEx/entrypoint.sh \
    && sed -i 's/app.run(host="127\.0\.0\.1",port=1234)/#app.run(host="127\.0\.0\.1",port=1234)/g; s/# app.run(host="0\.0\.0\.0", port = 5000)/app.run(host="0\.0\.0\.0", port = 5000)/g' ${WORKDIR}/chatGPTEx/main.py \
    && sed -i "s#program_dir+'/apikey.ini'#'/config/apikey.ini'#g" /app/chatGPTEx/main.py \
    && sed -i "s#program_dir+'/apikey.ini'#'/config/apikey.ini'#g" /app/chatGPTEx/search.py \
    && sed -i "s#os\.path\.join(program_dir, 'apikey.ini')#'/config/apikey.ini'#g" /app/chatGPTEx/search.py \
    && mkdir /config

EXPOSE 5000

VOLUME ["/config"]

ENTRYPOINT ["/app/chatGPTEx/entrypoint.sh"]
