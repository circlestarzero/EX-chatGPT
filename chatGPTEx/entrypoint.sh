#!/bin/sh
cd ${WORKDIR}

# 自动更新
if [ ! -s /tmp/requirements.txt.sha256sum ]; then
    sha256sum requirements.txt > /tmp/requirements.txt.sha256sum
fi
echo "更新..."
git remote set-url origin "${REPO_URL}" &> /dev/null
git clean -dffx
git fetch --depth 1 origin ${branch}
git reset --hard origin/${branch}
if [ $? -eq 0 ]; then
    echo "更新成功..."
    # Python依赖包更新
    hash_old=$(cat /tmp/requirements.txt.sha256sum)
    hash_new=$(sha256sum requirements.txt)
    if [ "${hash_old}" != "${hash_new}" ]; then
        echo "检测到requirements.txt有变化，重新安装依赖..."
        pip install --upgrade pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple/
        pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
        if [ $? -ne 0 ]; then
            echo "无法安装依赖，请更新镜像..."
        else
            echo "依赖安装成功..."
            sha256sum requirements.txt > /tmp/requirements.txt.sha256sum
            hash_old=$(cat /tmp/third_party.txt.sha256sum)
            hash_new=$(sha256sum third_party.txt)
        fi
    fi
else
    echo "更新失败，继续使用旧的程序来启动..."
fi

sed -i 's/app.run(host="127\.0\.0\.1",port=1234)/#app.run(host="127\.0\.0\.1",port=1234)/g; s/# app.run(host="0\.0\.0\.0", port = 5000)/app.run(host="0\.0\.0\.0", port = 5000)/g' /app/chatGPTEx/main.py

# 启动主程序
exec python /app/chatGPTEx/main.py
