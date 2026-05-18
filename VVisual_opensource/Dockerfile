# 基础镜像
ARG BASE
FROM ${BASE}
# 在容器内创建文件夹
RUN mkdir -p /app
# 设置容器工作目录
WORKDIR /app
# 复制所有文件
COPY . /app/
# 引入环境变量 CUSTOM_CMD =
ENV CUSTOM_CMD=""
# 安装依赖（可通过 PIP_INDEX_URL 环境变量指定私有 PyPI 镜像）
RUN pip3 install -r requirements.txt
# 启动python init
ENTRYPOINT ["/bin/sh", "-c", "python3 -u init.py ${CUSTOM_CMD}"]
