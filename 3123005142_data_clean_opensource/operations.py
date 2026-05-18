#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import uuid

import numpy as np
import pandas as pd
from minio import Minio
from minio.error import S3Error


def data_clean(data):
    """
    data_clean接口: 数据清洗

    data字典数据:
        input_url: str  原始 CSV 数据的网络链接

    返回数据中data字段必填并以约定格式返回data字典:
        output_url: str  清洗后 CSV 文件的本地路径
    """
    input_url = data.get("input_url")

    # 1. 从 URL 读取原始数据
    df = pd.read_csv(input_url)

    # 2. 去除完全重复的数据行
    df = df.drop_duplicates()

    # 3. 处理缺失值：移除 subclass 列中为空的行
    df = df.dropna(subset=["subclass"])

    # 4. 文本清洗：使用正则表达式保留中文、大小写字母和数字
    df["title"] = df["title"].str.replace(
        r"[^一-龥a-zA-Z0-9]", "", regex=True
    )

    # 5. 价格拆分
    def parse_price(price_str):
        price_str = str(price_str).strip()
        if "-" in price_str:
            parts = price_str.split("-")
            return float(parts[0]), float(parts[1])
        else:
            try:
                val = float(price_str)
                return val, val
            except ValueError:
                return np.nan, np.nan

    df["min_price"], df["max_price"] = zip(*df["price"].apply(parse_price))

    # 6. 保存清洗后的数据到本地
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "cleaned_data.csv")
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    # 7. 上传到 MinIO 获取可访问的网络链接
    output_url = upload_to_minio(output_path, bucket_name="data-clean")

    return {
        "msg": "success",
        "data": {
            "output_url": output_url
        }
    }


def upload_to_minio(local_file_path, bucket_name, object_name=None):
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    secure = os.getenv("MINIO_SECURE", "false").lower() == "true"

    minio_client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

    if object_name is None:
        file_extension = os.path.splitext(local_file_path)[1]
        object_name = f"{str(uuid.uuid4())}{file_extension}"

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    minio_client.fput_object(bucket_name, object_name, local_file_path)

    protocol = "https" if secure else "http"
    url = f"{protocol}://{endpoint}/{bucket_name}/{object_name}"
    return url

