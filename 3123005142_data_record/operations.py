#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import io
import os
import tempfile
import uuid

from minio import Minio

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "")
MINIO_SECURE = os.environ.get("MINIO_SECURE", "false").lower() == "true"
BUCKET_NAME = os.environ.get("MINIO_BUCKET", "tiaoma")


def _get_minio_client():
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )


def data_record(data):
    """
    data_record接口: 将图片URL与条码数字一一对应，生成CSV上传MinIO

    data字典数据:
        input_list: dict {图片URL: 条码数字}

    返回数据中data字段必填并以约定格式返回data字典:
        csvout_url: str CSV文件的MinIO URL

    """
    input_list = data.get("input_list")

    if not input_list:
        return {
            'msg': 'error: input_list 参数不能为空',
            'data': {'csvout_url': None}
        }

    if not isinstance(input_list, dict):
        return {
            'msg': 'error: input_list 格式错误，需要字典类型',
            'data': {'csvout_url': None}
        }

    try:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["image_url", "barcode"])
        for image_url, barcode in input_list.items():
            writer.writerow([image_url, barcode])
        csv_content = output.getvalue()
        output.close()

        tmp_dir = tempfile.mkdtemp()
        csv_path = os.path.join(tmp_dir, f"{uuid.uuid4()}.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(csv_content)

        client = _get_minio_client()
        object_name = f"{uuid.uuid4()}.csv"
        if not client.bucket_exists(BUCKET_NAME):
            client.make_bucket(BUCKET_NAME)
        client.fput_object(BUCKET_NAME, object_name, csv_path)

        csv_url = f"http://{MINIO_ENDPOINT}/{BUCKET_NAME}/{object_name}"
        return {
            'msg': 'success',
            'data': {'csvout_url': csv_url}
        }
    except Exception as e:
        return {
            'msg': f'error: {str(e)}',
            'data': {'csvout_url': None}
        }
