#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 4/11/25
# @Author  : luoolu
# @Github  : https://luoolu.github.io
# @Software: PyCharm
# @File    : parse_czi_zenlite.py
import os
import argparse
import logging
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


def save_metadata(czi_file, output_dir):
    """
    利用 AICSImageIO 从 CZI 文件中提取 XML 元数据，并保存到 output_dir/metadata.xml，返回 XML 字符串。
    如果 img.metadata 已为 Element，则转换为字符串。
    """
    img = AICSImage(czi_file)
    meta = img.metadata
    if isinstance(meta, ET.Element):
        # 转换为字符串（utf-8编码）
        xml_metadata = ET.tostring(meta, encoding='utf-8').decode('utf-8')
    else:
        try:
            xml_metadata = meta.raw  # 尝试获取 raw 属性
        except AttributeError:
            xml_metadata = str(meta)
    metadata_file = os.path.join(output_dir, "metadata.xml")
    try:
        with open(metadata_file, "w", encoding="utf-8") as f:
            f.write(xml_metadata)
        logging.info("元数据已保存至 %s", metadata_file)
    except Exception as e:
        logging.error("保存元数据失败: %s", e)
    return xml_metadata


def parse_xml_string(xml_input):
    """
    如果输入已经为 Element，则直接返回；
    否则将输入（字符串）解析为 Element 并返回。
    """
    if isinstance(xml_input, ET.Element):
        return xml_input
    xml_input = xml_input.replace('\x00', '').lstrip('\ufeff').strip()
    logging.info("元数据内容预览: %s", xml_input[:100])
    try:
        root = ET.fromstring(xml_input)
        return root
    except Exception as e:
        logging.error("XML 解析错误: %s", e)
        try:
            fixed_str = xml_input.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
            root = ET.fromstring(fixed_str)
            return root
        except Exception as e2:
            logging.error("重新编码后解析失败: %s", e2)
            raise e2


def parse_channels(xml_metadata):
    """
    从 XML 元数据中解析各通道信息，返回列表，每个元素为字典，包括：
      - name: 通道名称
      - is_activated: 是否激活（True/False）
      - is_selected: 是否采集（True/False）
    """
    channels_info = []
    try:
        root = parse_xml_string(xml_metadata)
        for track in root.findall(".//MultiTrackSetup/Track"):
            channels_node = track.find("Channels")
            if channels_node is not None:
                for channel in channels_node.findall("Channel"):
                    name = channel.attrib.get("Name", "").strip()
                    is_activated = channel.attrib.get("IsActivated", "false").strip().lower() == "true"
                    is_selected = channel.attrib.get("IsSelected", "false").strip().lower() == "true"
                    channels_info.append({
                        "name": name,
                        "is_activated": is_activated,
                        "is_selected": is_selected
                    })
        logging.info("解析到 %d 个通道信息", len(channels_info))
    except Exception as e:
        logging.error("解析通道信息失败: %s", e)
    return channels_info


def min_max_scale_to_8bit(image):
    """
    对图像进行简单的 min–max 归一化，将数值拉伸到 0～255，并转换为 uint8；
    若图像全像素一致，则返回全 0 图像。
    """
    arr = image.astype(np.float64)
    mn, mx = arr.min(), arr.max()
    if mx > mn:
        arr = (arr - mn) / (mx - mn) * 255.0
    return arr.astype(np.uint8)


def process_czi(czi_file, output_dir):
    """
    主流程：
      1. 利用 AICSImageIO 读取 CZI 文件，提取 XML 元数据与融合图数据；
      2. 解析 XML 获得通道信息；
      3. 检查融合数据形状：
         - 如果形状为 (1, C, Y, X, 3)，则说明包含彩色信息；
         - 如果形状为 (1, C, Y, X)（缺少 color 样本维度），则调用 czifile.asarray() 获取数据（通常返回 (1,C,Y,X,3)）。
      4. 针对每个通道：若像素全为 0则跳过，否则归一化（或直接保存），并利用 tifffile 保存为 BigTIFF/OME‑TIFF 文件。
    """
    # 使用 AICSImageIO 读取数据，指定维度顺序 "SCYX"，关闭 squeeze
    img = AICSImage(czi_file)
    xml_metadata = save_metadata(czi_file, output_dir)
    channels_info = parse_channels(xml_metadata)

    # 尝试用 AICSImageIO读取融合图数据
    fused_data = img.get_image_data("SCYX", squeeze=False, S=0, T=0)
    logging.info("AICSImageIO 返回融合图数据 shape: %s, dtype: %s", fused_data.shape, fused_data.dtype)

    # 检查是否包含样本（color）维度，即期望 shape 应为 (1, C, Y, X, 3)
    if fused_data.ndim == 5 and fused_data.shape[-1] == 3:
        data = fused_data[0]  # 去除 scene 维度，得到 (C, Y, X, 3)
        logging.info("使用 AICSImageIO 融合图数据，最终数据 shape: %s", data.shape)
    else:
        logging.warning("AICSImageIO 返回的数据 shape 为 %s，未检测到彩色样本维度，尝试使用 czifile", fused_data.shape)
        # 使用 czifile 获取数据，通常返回形状 (1, C, Y, X, 3)
        with CziFile(czi_file) as czi:
            data = czi.asarray()
        if data.ndim == 5:
            data = data[0]
            logging.info("使用 czifile 得到融合图数据，最终数据 shape: %s", data.shape)
        else:
            logging.error("无法获取正确形状的数据，退出")
            return

    # 预期 data 形状为 (C, Y, X, 3)
    if data.ndim != 4 or data.shape[-1] != 3:
        logging.error("期望数据形状为 (C, Y, X, 3)，但实际为: %s", data.shape)
        return

    num_channels = data.shape[0]
    logging.info("检测到 %d 个通道", num_channels)
    if len(channels_info) != num_channels:
        logging.warning("元数据中解析到的通道数量 (%d) 与融合数据中 (%d) 不匹配",
                        len(channels_info), num_channels)
    for ch in range(num_channels):
        ch_info = channels_info[ch] if ch < len(channels_info) else {"name": f"channel_{ch}", "is_selected": False}
        channel_data = data[ch]  # shape: (Y, X, 3)
        ch_min, ch_max = channel_data.min(), channel_data.max()
        logging.info("通道 %d (%s) 数据范围: min=%.3f, max=%.3f", ch, ch_info.get("name", f"channel_{ch}"), ch_min,
                     ch_max)
        if ch_max == 0:
            logging.info("通道 %d (%s) 像素全为0，跳过保存", ch, ch_info.get("name", f"channel_{ch}"))
            continue
        # 对图像归一化（如果原数据已为 uint8 且 0~255，可省略归一化步骤）
        channel_8bit = min_max_scale_to_8bit(channel_data)
        output_filename = f"{ch_info.get('name', f'channel_{ch}')}.ome.tif"
        output_path = os.path.join(output_dir, output_filename)
        try:
            tifffile.imwrite(output_path, channel_8bit, bigtiff=True, photometric="rgb")
            logging.info("保存通道 %d (%s) 图像至: %s", ch, ch_info.get("name", f"channel_{ch}"), output_path)
        except Exception as e:
            logging.error("保存通道 %d (%s) 图像失败: %s", ch, ch_info.get("name", f"channel_{ch}"), e)


def main():
    parser = argparse.ArgumentParser(
        description="利用 AICSImageIO 或 czifile 从 CZI 文件中获取融合图（彩色）数据，并输出各通道图像（归一化后，支持超大图保存）"
    )
    parser.add_argument("czi_file", type=str, help="输入 CZI 文件路径")
    parser.add_argument("output_dir", type=str, help="输出目录路径")
    args = parser.parse_args()
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    process_czi(args.czi_file, args.output_dir)


if __name__ == "__main__":
    main()