# picture_clean — 图片解压组件

从 MinIO 下载 zip 文件，解压后将其中所有文件逐一上传到 MinIO，返回文件 URL 列表。

## 在流程中的角色

接收 file_upload 生成的 zip URL，下载并解压，将每张条形码图片分别上传，URL 列表传入 digital_recognition 进行识别。

## 接口

| 方向 | 字段 | 类型 | 说明 |
|------|------|------|------|
| 入参 | `input_url` | string | zip 文件的 MinIO URL |
| 出参 | `output_url` | list[string] | 解压后所有文件的 MinIO URL 列表 |

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
python -u init.py '{"isdp.instance-id":"picture_clean_1","isdp.nacos":"<nacos_addr>","isdp.instance-ip":"<your_ip>"}'
```

## Docker 构建

```bash
docker build --build-arg BASE=python:3.11-slim -t picture_clean .
```

## 依赖

- nacos-sdk-python
- paho-mqtt
- minio
- redis
