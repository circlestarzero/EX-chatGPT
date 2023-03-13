#!/bin/sh
cd ${WORKDIR}

# 自动更新
git pull
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
        hash_old=$(cat /tmp/third_party.txt.sha256sum)
        hash_new=$(sha256sum third_party.txt)
        if [ "${hash_old}" != "${hash_new}" ]; then
            echo "检测到third_party.txt有变化，更新第三方组件..."
            git submodule update --init --recursive
            if [ $? -ne 0 ]; then
                echo "无法更新第三方组件，请更新镜像..."
            else
                echo "第三方组件安装成功..."
                sha256sum third_party.txt > /tmp/third_party.txt.sha256sum
            fi
        fi
    fi
fi
# 启动主程序
exec python /app/chatGPTEx/main.py
