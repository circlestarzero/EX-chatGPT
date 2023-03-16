#!/bin/sh
cd ${WORKDIR}

# 自动更新
if [ "${AUTO_UPDATE}" = "true" ]; then
    if [ ! -s /tmp/requirements.txt.sha256sum ]; then
        sha256sum /app/chatGPTEx/requirements.txt > /tmp/requirements.txt.sha256sum
    fi
    echo "更新源码"
    branch=main
    git clean -dffx
    git fetch --depth 1 origin ${branch}
    git reset --hard origin/${branch}
    if [ $? -eq 0 ]; then
        echo "源码更新成功"
        chmod +x ${WORKDIR}/chatGPTEx/entrypoint.sh
        sed -i 's/app.run(host="127\.0\.0\.1",port=1234)/#app.run(host="127\.0\.0\.1",port=1234)/g; s/# app.run(host="0\.0\.0\.0", port = 5000)/app.run(host="0\.0\.0\.0", port = 5000)/g' ${WORKDIR}/chatGPTEx/main.py
        sed -i "s#program_dir+'/apikey.ini'#'/config/apikey.ini'#g" /app/chatGPTEx/main.py
        sed -i "s#program_dir+'/apikey.ini'#'/config/apikey.ini'#g" /app/chatGPTEx/search.py
        sed -i "s#os\.path\.join(program_dir, 'apikey.ini')#'/config/apikey.ini'#g" /app/chatGPTEx/search.py
        echo "Python更新依赖包"
        hash_old=$(cat /tmp/requirements.txt.sha256sum)
        hash_new=$(sha256sum requirements.txt)
        if [ "${hash_old}" != "${hash_new}" ]; then
            echo "检测到requirements.txt有变化，重新安装依赖..."
            pip install -r /app/chatGPTEx/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
            if [ $? -ne 0 ]; then
                echo "无法安装依赖，请更新镜像..."
            else
                echo "依赖安装成功..."
                sha256sum /app/chatGPTEx/requirements.txt > /tmp/requirements.txt.sha256sum
            fi
        fi
    else
        echo "更新失败"
    fi
else
    echo "程序自动升级已关闭，如需自动升级请在创建容器时设置环境变量：AUTO_UPDATE=true"
fi
# 启动主程序
exec python /app/chatGPTEx/main.py
