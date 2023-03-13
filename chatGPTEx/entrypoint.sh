#!/bin/sh
cd ${WORKDIR}

# 自动更新
git config pull.rebase false
if [ ! -s /tmp/requirements.txt.sha256sum ]; then
    sha256sum /app/chatGPTEx/requirements.txt > /tmp/requirements.txt.sha256sum
fi
hash_old=$(cat /tmp/requirements.txt.sha256sum)
hash_new=$(sha256sum requirements.txt)
if [ "${hash_old}" != "${hash_new}" ]; then
    echo "检测到requirements.txt有变化，重新安装依赖..."
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
    if [ $? -ne 0 ]; then
        echo "无法安装依赖，请更新镜像..."
    else
        echo "依赖安装成功..."
        sha256sum requirements.txt > /tmp/requirements.txt.sha256sum
    fi
fi
# 启动主程序
exec python /app/chatGPTEx/main.py
