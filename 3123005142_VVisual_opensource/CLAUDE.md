# MQTT 微服务组件框架

## 架构

```
MQTT 消息 → server.py (消息路由) → routes.py (匹配主题) → operations.py (业务函数)
```

- 每个组件一个 server_id，通过 MQTT 主题通信
- 接收主题: `e/req/{server_id}/{operation}`
- 响应主题: `e/resp/{server_id}/{operation}`
- 启动命令: `python -u init.py '{json配置}'`

## operations.py 约定

- 入参: `data` dict，约定 key `input_url: str`（MinIO 上的数据文件 URL）
- 返回: `{'msg': 'success', 'data': {'output_url': str}}`（处理结果上传 MinIO 后的 URL）
- 异常由 server.py 统一捕获，返回 code=500

## MinIO 配置

通过环境变量配置，支持公有云 / 私有化部署：

```python
from minio import Minio
client = Minio(
    os.getenv("MINIO_ENDPOINT", "play.min.io:9000"),
    access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    secure=False,
)
```
- Bucket: `data-clean`（需设公开读）
- 输出文件上传到此 bucket，返回 `{MINIO_ENDPOINT}/{bucket}/{filename}`

## 新增 operation 步骤

1. 在 `operations.py` 写函数（遵循入参/返回约定）
2. 在 `routes.py` 的 `list` 中添加 `Route(desc="", operation="函数名")`
3. 如需新依赖，加到 `requirements.txt`

## 数据 schema（data.csv 清洗后）

```
title, href, date, city, theatre, price, type, subclass, status, min_price, max_price
```

- title: 清洗后纯中英文数字
- price: 原始价格区间字符串
- min_price/max_price: 拆分后的数值
- subclass: 子类别（音乐节/话剧/其他等）
- city: 演出城市

## 本地环境

```bash
cd {项目目录}
venv/Scripts/python -m pip install -r requirements.txt  # 首次
venv/Scripts/python -u init.py '{json启动参数}'
```

## 测试方法

直接调用 `operations.函数名({"input_url": "本地路径或MinIO URL"})`，验证返回的 output_url。
