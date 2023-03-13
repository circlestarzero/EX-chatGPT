#!/bin/sh
cd ${WORKDIR}

sed -i 's/app.run(host="127\.0\.0\.1",port=1234)/#app.run(host="127\.0\.0\.1",port=1234)/g; s/# app.run(host="0\.0\.0\.0", port = 5000)/app.run(host="0\.0\.0\.0", port = 5000)/g' /app/chatGPTEx/main.py

# 启动主程序
exec python /app/chatGPTEx/main.py
