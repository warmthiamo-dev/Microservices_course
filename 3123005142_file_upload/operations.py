#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import uuid

from minio import Minio

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "")
MINIO_SECURE = os.environ.get("MINIO_SECURE", "false").lower() == "true"
BUCKET_NAME = os.environ.get("MINIO_BUCKET", "tiaoma")


def upload_to_minio(local_file_path, bucket_name, object_name=None):
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )
    if object_name is None:
        file_extension = os.path.splitext(local_file_path)[1]
        object_name = f"{str(uuid.uuid4())}{file_extension}"

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    minio_client.fput_object(bucket_name, object_name, local_file_path)

    protocol = "https" if MINIO_SECURE else "http"
    url = f"{protocol}://{MINIO_ENDPOINT}/{bucket_name}/{object_name}"
    return url


def _resolve_path(file_path):
    """解析文件路径，兼容Docker和本地运行环境"""
    if os.path.isfile(file_path):
        return file_path
    basename = os.path.basename(file_path)
    cwd_path = os.path.join(os.getcwd(), basename)
    if os.path.isfile(cwd_path):
        return cwd_path
    return file_path


def file_opload(data):
    """
    file_opload接口: 将本地文件上传到MinIO并返回访问URL

    data字典数据:
        file_path: str 本地文件路径

    返回数据中data字段必填并以约定格式返回data字典:
        output_path: str MinIO文件访问URL

    """
    file_path = data.get("file_path")

    if not file_path:
        return {
            'msg': 'error: file_path 参数不能为空',
            'data': {'output_path': None}
        }

    file_path = _resolve_path(file_path)

    if not os.path.isfile(file_path):
        return {
            'msg': f'error: 文件不存在: {file_path}',
            'data': {'output_path': None}
        }

    try:
        url = upload_to_minio(file_path, BUCKET_NAME)
        return {
            'msg': 'success',
            'data': {'output_path': url}
        }
    except Exception as e:
        return {
            'msg': f'error: 上传MinIO失败: {str(e)}',
            'data': {'output_path': None}
        }
