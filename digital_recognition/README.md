# digital_recognition — 数字条码识别组件

下载条形码图片并使用 OpenCV 进行识别，提取其中的数字，返回图片 URL 与条码数字的映射字典。

## 在流程中的角色

接收 picture_clean 解压出的图片 URL 列表，逐张下载识别，将结果（图片 URL → 条码数字）以字典形式传递给 data_record 组件。

## 接口

| 方向 | 字段 | 类型 | 说明 |
|------|------|------|------|
| 入参 | `input_url` | list[string] | 条形码图片的 MinIO URL 列表 |
| 出参 | `output_url` | dict | `{图片URL: 条码数字}` 映射字典 |

### 出参示例

```json
{
  "output_url": {
    "http://minio:9000/tiaoma/xxx.jpg": 4902520242204,
    "http://minio:9000/tiaoma/yyy.jpg": 6901234567890
  }
}
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MINIO_ENDPOINT` | `localhost:9000` | MinIO 服务地址 |
| `MINIO_ACCESS_KEY` | `minioadmin` | MinIO Access Key |
| `MINIO_SECRET_KEY` | (必填) | MinIO Secret Key |
| `MINIO_SECURE` | `false` | 是否使用 HTTPS |

## 本地启动

```bash
pip install -r requirements.txt
python -u init.py '{"isdp.instance-id":"digital_recognition_1","isdp.nacos":"<nacos_addr>","isdp.instance-ip":"<your_ip>"}'
```

## Docker 构建

```bash
docker build --build-arg BASE=python:3.11-slim -t digital_recognition .
```

## 依赖

- nacos-sdk-python
- paho-mqtt
- minio
- opencv-python-headless
- redis
