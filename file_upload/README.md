# file_upload — 文件上传组件

将本地文件上传到 MinIO 对象存储，返回文件访问 URL。

## 在流程中的角色

作为流水线的第一个组件，接收本地 zip 文件路径，上传至 MinIO 并返回 URL，供下游组件（picture_clean）下载处理。

## 接口

| 方向 | 字段 | 类型 | 说明 |
|------|------|------|------|
| 入参 | `file_path` | string | 本地文件路径 |
| 出参 | `output_path` | string | MinIO 文件访问 URL |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MINIO_ENDPOINT` | `localhost:9000` | MinIO 服务地址 |
| `MINIO_ACCESS_KEY` | `minioadmin` | MinIO Access Key |
| `MINIO_SECRET_KEY` | (必填) | MinIO Secret Key |
| `MINIO_BUCKET` | `tiaoma` | 目标 Bucket 名称 |
| `MINIO_SECURE` | `false` | 是否使用 HTTPS |

## 本地启动

```bash
pip install -r requirements.txt
python -u init.py '{"isdp.instance-id":"file_upload_1","isdp.nacos":"<nacos_addr>","isdp.instance-ip":"<your_ip>"}'
```

## Docker 构建

```bash
docker build --build-arg BASE=python:3.11-slim -t file_upload .
```

## 依赖

- nacos-sdk-python
- paho-mqtt
- minio
- redis
