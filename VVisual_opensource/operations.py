#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import uuid
from collections import Counter

import matplotlib
matplotlib.use("Agg")  # 非交互后端，避免 tkinter 多线程问题

import jieba
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from minio import Minio

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "WenQuanYi Micro Hei"]
plt.rcParams["axes.unicode_minus"] = False

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def _get_minio_client():
    return Minio(
        os.getenv("MINIO_ENDPOINT", "play.min.io:9000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        secure=False,
    )


def _upload(local_path, object_name=None):
    client = _get_minio_client()
    bucket = "data-clean"
    if object_name is None:
        ext = os.path.splitext(local_path)[1]
        object_name = f"{str(uuid.uuid4())}{ext}"
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
    client.fput_object(bucket, object_name, local_path)
    endpoint = os.getenv("MINIO_ENDPOINT", "play.min.io:9000")
    return f"http://{endpoint}/{bucket}/{object_name}"


def all_visual(data):
    input_url = data.get("input_url")
    if not input_url:
        raise ValueError("缺少必填参数 input_url，请检查组件连线是否正确")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(input_url)

    # ========== 1. 城市占比玫瑰图 ==========
    city_counts = df["city"].value_counts().head(15)
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection="polar"))
    theta = np.linspace(0, 2 * np.pi, len(city_counts), endpoint=False)
    width = 2 * np.pi / len(city_counts)
    bars = ax.bar(theta, city_counts.values, width=width, bottom=0, alpha=0.8)
    for t, v, bar in zip(theta, city_counts.values, bars):
        ax.text(t, v + 2, f"{v}", ha="center", va="bottom", fontsize=9)
    ax.set_xticks(theta)
    ax.set_xticklabels(city_counts.index, fontsize=10)
    ax.set_title("城市占比玫瑰图", fontsize=16, pad=30)
    city_path = os.path.join(OUTPUT_DIR, "city_rose.png")
    fig.savefig(city_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    output_city_url = _upload(city_path)

    # ========== 2. 词频率统计柱状图 ==========
    STOP_WORDS = {"的", "了", "在", "是", "和", "与", "及", "·", " ", "-", "—",
                  "《", "》", "》", "•", "（", "）", "、", "。", "！", "？"}
    all_words = []
    for title in df["title"].astype(str):
        words = jieba.lcut(title)
        all_words.extend([w for w in words if len(w) >= 2 and w not in STOP_WORDS])
    word_freq = Counter(all_words).most_common(20)
    labels, values = zip(*word_freq) if word_freq else ([], [])

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.barh(range(len(labels)), values, alpha=0.8)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("出现次数", fontsize=12)
    ax.set_title("词频率统计柱状图 (Top 20)", fontsize=16)
    for i, v in enumerate(values):
        ax.text(v + 1, i, str(v), va="center", fontsize=9)
    words_path = os.path.join(OUTPUT_DIR, "words_bar.png")
    fig.savefig(words_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    ouput_words_url = _upload(words_path)

    # ========== 3. 演唱会子类饼图 ==========
    concert_df = df[df["type"] == "演唱会"]
    subclass_counts = concert_df["subclass"].value_counts()
    fig, ax = plt.subplots(figsize=(10, 8))
    wedges, texts, autotexts = ax.pie(
        subclass_counts.values,
        labels=subclass_counts.index,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.6,
    )
    for t in autotexts:
        t.set_fontsize(10)
    ax.set_title("演唱会子类分布饼图", fontsize=16)
    subclass_path = os.path.join(OUTPUT_DIR, "subclass_pie.png")
    fig.savefig(subclass_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    output_subclass_url = _upload(subclass_path)

    # ========== 4. 最高价格与演出关系图 ==========
    top_price = df.nlargest(20, "max_price")[["title", "max_price", "city"]].copy()
    fig, ax = plt.subplots(figsize=(14, 8))
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(top_price)))
    bars = ax.bar(range(len(top_price)), top_price["max_price"].values, color=colors, alpha=0.85)
    ax.set_xticks(range(len(top_price)))
    short_labels = [t[:12] + "..." if len(str(t)) > 12 else t for t in top_price["title"].values]
    ax.set_xticklabels(short_labels, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("最高票价 (元)", fontsize=12)
    ax.set_title("最高价格 Top 20 演出", fontsize=16)
    for i, (v, city) in enumerate(zip(top_price["max_price"].values, top_price["city"].values)):
        ax.text(i, v + 10, f"{v:.0f}\n{city}", ha="center", fontsize=8)
    price_path = os.path.join(OUTPUT_DIR, "price_chart.png")
    fig.savefig(price_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    output_price_url = _upload(price_path)

    return {
        "msg": "success",
        "data": {
            "output_city_url": output_city_url,
            "ouput_words_url": ouput_words_url,
            "output_subclass_url": output_subclass_url,
            "output_price_url": output_price_url,
        }
    }
