#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import tempfile
import uuid
import zipfile
from urllib.parse import urlparse

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


def _parse_minio_url(url):
    """从MinIO URL中解析出bucket和object_name"""
    parsed = urlparse(url)
    path = parsed.path.lstrip("/")
    parts = path.split("/", 1)
    bucket = parts[0] if parts else ""
    object_name = parts[1] if len(parts) > 1 else ""
    return bucket, object_name


def upload_to_minio(local_file_path, bucket_name, object_name=None):
    client = _get_minio_client()
    if object_name is None:
        file_extension = os.path.splitext(local_file_path)[1]
        object_name = f"{str(uuid.uuid4())}{file_extension}"

    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)

    client.fput_object(bucket_name, object_name, local_file_path)

    protocol = "https" if MINIO_SECURE else "http"
    url = f"{protocol}://{MINIO_ENDPOINT}/{bucket_name}/{object_name}"
    return url


def picture_clean(data):
    """
    picture_clean接口: 下载zip文件，解压后逐文件上传到MinIO，返回URL列表

    data字典数据:
        input_url: str zip文件的MinIO URL

    返回数据中data字段必填并以约定格式返回data字典:
        output_url: list MinIO文件访问URL列表

    """
    input_url = data.get("input_url")

    if not input_url:
        return {
            'msg': 'error: input_url 参数不能为空',
            'data': {'output_url': []}
        }

    tmp_dir = tempfile.mkdtemp()

    try:
        bucket, object_name = _parse_minio_url(input_url)
        if not bucket or not object_name:
            return {
                'msg': f'error: 无法解析MinIO URL: {input_url}',
                'data': {'output_url': []}
            }

        client = _get_minio_client()
        zip_path = os.path.join(tmp_dir, "input.zip")
        client.fget_object(bucket, object_name, zip_path)

        if not zipfile.is_zipfile(zip_path):
            return {
                'msg': 'error: 下载的文件不是有效的zip',
                'data': {'output_url': []}
            }

        extract_dir = os.path.join(tmp_dir, "extracted")
        os.makedirs(extract_dir)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        urls = []
        for root, dirs, files in os.walk(extract_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                url = upload_to_minio(file_path, BUCKET_NAME)
                urls.append(url)

        return {
            'msg': 'success',
            'data': {'output_url': urls}
        }
    except Exception as e:
        return {
            'msg': f'error: {str(e)}',
            'data': {'output_url': []}
        }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
