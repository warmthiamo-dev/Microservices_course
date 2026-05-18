# data_record — 数据记录组件

将图片 URL 与条码识别结果一一对应，生成 CSV 文件上传到 MinIO，返回 CSV 的访问 URL。

## 在流程中的角色

作为流水线的最后一个组件，接收 digital_recognition 的映射字典，生成规范的 CSV 记录（image_url, barcode），上传后返回 URL 供下载。

## 接口

| 方向 | 字段 | 类型 | 说明 |
|------|------|------|------|
| 入参 | `input_list` | dict | `{图片URL: 条码数字}` 映射字典 |
| 出参 | `csvout_url` | string | 生成的 CSV 文件 MinIO URL |

### CSV 格式

```csv
image_url,barcode
http://minio:9000/tiaoma/xxx.jpg,4902520242204
http://minio:9000/tiaoma/yyy.jpg,6901234567890
```

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
python -u init.py '{"isdp.instance-id":"data_record_1","isdp.nacos":"<nacos_addr>","isdp.instance-ip":"<your_ip>"}'
```

## Docker 构建

```bash
docker build --build-arg BASE=python:3.11-slim -t data_record .
```

## 依赖

- nacos-sdk-python
- paho-mqtt
- minio
- redis
