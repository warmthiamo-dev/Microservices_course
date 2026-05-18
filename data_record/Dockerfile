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
# 安装依赖 (设置 PIP_INDEX_URL 可切换私有源)
ARG PIP_INDEX_URL=https://pypi.org/simple
RUN pip3 install --index-url ${PIP_INDEX_URL} -r requirements.txt
# 启动python init
ENTRYPOINT ["/bin/sh", "-c", "python3 -u init.py ${CUSTOM_CMD}"]
