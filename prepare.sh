#!/bin/bash
# prepare.sh文件为云开发平台构建用户自定义镜像的前置操作，处理环境变量以及启动命令等操作

## 此处不要改动 ------
echo "#!/bin/bash" > start.sh
# 设置环境变量
index=0
for item in $*
do
  let index+=1
  if [ $index -ge 2 ]; then
    echo " ${item}"
    echo "export ${item}" >> start.sh
  fi
done
## ------ 此处不要改动

## 自定义命令 ------
echo "gunicorn main:app -b 0.0.0.0:8080 -w 4" >> start.sh
## ------自定义命令