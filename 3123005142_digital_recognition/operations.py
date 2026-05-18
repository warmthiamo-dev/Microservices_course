#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import tempfile
from urllib.parse import urlparse

import cv2
from minio import Minio

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "")
MINIO_SECURE = os.environ.get("MINIO_SECURE", "false").lower() == "true"


def _get_minio_client():
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )


def _parse_minio_url(url):
    parsed = urlparse(url)
    path = parsed.path.lstrip("/")
    parts = path.split("/", 1)
    bucket = parts[0] if parts else ""
    object_name = parts[1] if len(parts) > 1 else ""
    return bucket, object_name


def digital_recognition(data):
    """
    digital_recognition接口: 下载条形码图片，识别其中的数字条码

    data字典数据:
        input_url: list MinIO图片URL列表

    返回数据中data字段必填并以约定格式返回data字典:
        output_url: dict {图片URL: 识别出的数字}

    """
    input_url = data.get("input_url")

    if not input_url:
        return {
            'msg': 'error: input_url 参数不能为空',
            'data': {'output_url': {}}
        }

    if not isinstance(input_url, list):
        input_url = [input_url]

    client = _get_minio_client()
    tmp_dir = tempfile.mkdtemp()
    results = {}

    try:
        for url in input_url:
            bucket, object_name = _parse_minio_url(url)
            if not bucket or not object_name:
                continue

            file_name = object_name.split("/")[-1]
            local_path = os.path.join(tmp_dir, file_name)
            client.fget_object(bucket, object_name, local_path)

            img = cv2.imread(local_path)
            if img is None:
                continue
            detector = cv2.barcode.BarcodeDetector()
            retval, points, straight_code = detector.detectAndDecode(img)
            if retval and retval.isdigit():
                results[url] = int(retval)

        return {
            'msg': 'success',
            'data': {'output_url': results}
        }
    except Exception as e:
        return {
            'msg': f'error: {str(e)}',
            'data': {'output_url': {}}
        }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
