#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 7/24/25
# @Author  : LOOLO
# @Software: PyCharm
# @File    : parse_czi_zenlite_ultrafast.py

import os
import argparse
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
import gc

import numpy as np
import xml.etree.ElementTree as ET
import tifffile

from aicsimageio import AICSImage
from czifile import CziFile

# 配置日志
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

# 性能配置
MAX_WORKERS = min(cpu_count(), 8)


def save_metadata_fast(czi_file, output_dir):
    """快速元数据保存"""
    start_time = time.perf_counter()

    try:
        img = AICSImage(czi_file)
        meta = img.metadata

        if isinstance(meta, ET.Element):
            xml_metadata = ET.tostring(meta, encoding='utf-8').decode('utf-8')
        else:
            try:
                xml_metadata = meta.raw
            except AttributeError:
                xml_metadata = str(meta)

        metadata_file = os.path.join(output_dir, "metadata.xml")
        with open(metadata_file, "w", encoding="utf-8") as f:
            f.write(xml_metadata)

        elapsed = time.perf_counter() - start_time
        logging.info(f"元数据保存完成，耗时: {elapsed:.2f}秒")
        return xml_metadata

    except Exception as e:
        logging.error(f"保存元数据失败: {e}")
        return ""


def parse_channels_fast(xml_metadata):
    """快速通道解析"""
    channels_info = []
    try:
        if isinstance(xml_metadata, ET.Element):
            root = xml_metadata
        else:
            xml_clean = xml_metadata.replace('\x00', '').lstrip('\ufeff').strip()
            root = ET.fromstring(xml_clean)

        for track in root.findall(".//MultiTrackSetup/Track"):
            channels_node = track.find("Channels")
            if channels_node is not None:
                for channel in channels_node.findall("Channel"):
                    name = channel.attrib.get("Name", "").strip()
                    channels_info.append({"name": name})

        logging.info(f"解析到 {len(channels_info)} 个通道")
    except Exception as e:
        logging.error(f"解析通道失败: {e}")

    return channels_info


def simple_normalize(image):
    """极简归一化"""
    if image.dtype == np.uint8:
        return image

    arr = image.astype(np.float32)
    mn, mx = arr.min(), arr.max()

    if mx > mn:
        arr = (arr - mn) / (mx - mn) * 255.0
        return arr.astype(np.uint8)
    else:
        return np.zeros_like(image, dtype=np.uint8)


def save_single_channel(args):
    """保存单个通道"""
    ch_idx, channel_data, ch_name, output_dir = args

    try:
        # 检查数据
        ch_max = np.max(channel_data)
        if ch_max == 0:
            logging.info(f"通道 {ch_idx} ({ch_name}) 全零，跳过")
            return False

        # 归一化
        channel_8bit = simple_normalize(channel_data)

        # 保存
        output_filename = f"{ch_name}.ome.tif"
        output_path = os.path.join(output_dir, output_filename)

        # 检查图像大小，对于超大图像使用 BigTIFF 格式
        image_size = channel_8bit.nbytes
        use_bigtiff = image_size > 2 ** 31  # 2GB 阈值

        # 简化保存选项，确保支持大文件
        if channel_8bit.ndim == 3 and channel_8bit.shape[-1] == 3:
            photometric = "rgb"
        else:
            photometric = "minisblack"

        # 使用优化的保存参数处理超大图像
        tifffile.imwrite(
            output_path,
            channel_8bit,
            bigtiff=use_bigtiff,  # 自动决定是否使用 BigTIFF
            photometric=photometric,
            compression='lzw',
            tile=(512, 512) if image_size > 100 * 1024 * 1024 else None,  # 大于100MB使用分块
            predictor=2 if photometric == "rgb" else None
        )

        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logging.info(f"已保存通道 {ch_idx} ({ch_name}), 文件大小: {file_size_mb:.1f}MB")
        return True

    except Exception as e:
        logging.error(f"保存通道 {ch_idx} ({ch_name}) 失败: {e}")
        # 如果是格式错误，尝试强制使用 BigTIFF
        if "'I' format requires" in str(e):
            try:
                logging.info(f"尝试强制使用 BigTIFF 保存通道 {ch_idx}")
                tifffile.imwrite(
                    output_path,
                    channel_8bit,
                    bigtiff=True,  # 强制使用 BigTIFF
                    photometric=photometric,
                    tile=(512, 512)  # 强制分块
                )
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                logging.info(f"BigTIFF 保存成功: 通道 {ch_idx} ({ch_name}), 文件大小: {file_size_mb:.1f}MB")
                return True
            except Exception as e2:
                logging.error(f"BigTIFF 保存也失败: {e2}")
        return False


def process_czi_ultrafast(czi_file, output_dir):
    """超快速 CZI 处理"""
    total_start = time.perf_counter()

    logging.info(f"开始处理: {czi_file}")

    # 1. 快速保存元数据
    xml_metadata = save_metadata_fast(czi_file, output_dir)
    channels_info = parse_channels_fast(xml_metadata)

    # 2. 直接使用 czifile 快速读取
    logging.info("使用 czifile 快速读取数据...")
    load_start = time.perf_counter()

    try:
        with CziFile(czi_file) as czi:
            # 直接读取，不做复杂处理
            data = czi.asarray()
            logging.info(f"原始数据形状: {data.shape}, 类型: {data.dtype}")

            # 简单降维
            while data.ndim > 4:
                data = data[0]

            # 如果是 (C, Y, X) 格式，添加颜色维度
            if data.ndim == 3:
                # 转换为 (C, Y, X, 3)
                data = np.stack([data, data, data], axis=-1)
            elif data.ndim == 4 and data.shape[-1] == 1:
                # (C, Y, X, 1) -> (C, Y, X, 3)
                data = np.repeat(data, 3, axis=-1)

            logging.info(f"处理后数据形状: {data.shape}")

    except Exception as e:
        logging.error(f"czifile 读取失败: {e}")

        # 备选方案：使用 AICSImageIO
        logging.info("尝试 AICSImageIO...")
        try:
            img = AICSImage(czi_file)
            data = img.data

            # 简单处理维度
            while data.ndim > 4:
                data = data[0]

            if data.ndim == 3:
                data = np.stack([data, data, data], axis=-1)

            logging.info(f"AICSImageIO 数据形状: {data.shape}")

        except Exception as e2:
            logging.error(f"所有方法都失败了: {e2}")
            return

    load_time = time.perf_counter() - load_start
    logging.info(f"数据加载耗时: {load_time:.2f}秒")

    # 3. 快速并行保存
    process_start = time.perf_counter()

    num_channels = data.shape[0]
    logging.info(f"开始处理 {num_channels} 个通道")

    # 准备参数
    tasks = []
    for ch_idx in range(num_channels):
        ch_name = channels_info[ch_idx]["name"] if ch_idx < len(channels_info) else f"channel_{ch_idx}"
        tasks.append((ch_idx, data[ch_idx], ch_name, output_dir))

    # 并行处理
    success_count = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(save_single_channel, tasks)
        success_count = sum(results)

    process_time = time.perf_counter() - process_start
    total_time = time.perf_counter() - total_start

    logging.info("=" * 50)
    logging.info("处理完成")
    logging.info(f"数据加载: {load_time:.2f}秒")
    logging.info(f"通道处理: {process_time:.2f}秒")
    logging.info(f"总耗时: {total_time:.2f}秒")
    logging.info(f"成功处理: {success_count}/{num_channels} 个通道")
    logging.info("=" * 50)


def main():
    global MAX_WORKERS

    parser = argparse.ArgumentParser(description="超高速 CZI 文件解析器")
    parser.add_argument("czi_file", help="CZI文件路径")
    parser.add_argument("output_dir", help="输出目录")
    parser.add_argument("--max-workers", type=int, default=8, help="最大工作线程数")

    args = parser.parse_args()

    if not os.path.exists(args.czi_file):
        logging.error(f"文件不存在: {args.czi_file}")
        return

    os.makedirs(args.output_dir, exist_ok=True)
    MAX_WORKERS = args.max_workers

    logging.info(f"系统: CPU={cpu_count()}核, 工作线程={MAX_WORKERS}")

    process_czi_ultrafast(args.czi_file, args.output_dir)


if __name__ == "__main__":
    main()