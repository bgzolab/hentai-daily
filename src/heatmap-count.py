#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author : bGZo
@Date : 2025-06-19
@Links : https://github.com/bGZo
"""
import os
import json
from pathlib import Path
from datetime import datetime


def scan_directories(root_path="api/archives/", output_file="api/count.json"):
    """
    遍历年/月/日.json的目录结构，统计每个日期的文件数量

    Args:
        root_path: 根目录路径，默认为当前目录
        output_file: 输出的JSON文件名
    """
    statistics = []

    # 获取根目录路径
    root = Path(root_path)

    # 遍历年份目录
    for year_dir in sorted(root.iterdir()):
        if not year_dir.is_dir():
            continue

        # 检查是否为年份目录（4位数字）
        if not year_dir.name.isdigit() or len(year_dir.name) != 4:
            continue

        year = year_dir.name
        print(f"处理年份: {year}")

        # 遍历月份目录
        for month_dir in sorted(year_dir.iterdir()):
            if not month_dir.is_dir():
                continue

            # 检查是否为月份目录（1-2位数字）
            if not month_dir.name.isdigit():
                continue

            month = month_dir.name.zfill(2)  # 补零确保两位数
            print(f"  处理月份: {month}")

            # 遍历日期文件
            for day_file in sorted(month_dir.iterdir()):
                if not day_file.is_file():
                    continue

                # 检查是否为.json文件
                if not day_file.name.endswith('.json'):
                    continue

                # 提取日期（去掉.json后缀）
                day = day_file.stem

                # 验证日期格式
                if not day.isdigit():
                    continue

                day = day.zfill(2)  # 补零确保两位数

                # 构造日期字符串
                date_str = f"{year}-{month}-{day}"

                # 验证日期是否有效
                try:
                    datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    print(f"    跳过无效日期: {date_str}")
                    continue

                print(f"    找到文件: {date_str}")

                # 添加到统计数据中
                # 这里假设每个文件代表1个单位，你可以根据需要修改这个逻辑
                # 比如读取JSON文件内容来统计具体数量
                statistics.append({
                    "date": date_str,
                    "value": 1  # 可以根据实际需求修改这个值
                })

    # 按日期排序
    statistics.sort(key=lambda x: x["date"])

    # 输出到JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(statistics, f, ensure_ascii=False, indent=2)

    print(f"\n统计完成！共处理 {len(statistics)} 个日期")
    print(f"结果已保存到: {output_file}")

    # 显示前几条和后几条记录作为预览
    if statistics:
        print("\n预览（前5条）:")
        for item in statistics[:5]:
            print(f"  {item}")

        if len(statistics) > 10:
            print("\n预览（后5条）:")
            for item in statistics[-5:]:
                print(f"  {item}")


def count_json_content(file_path):
    """
    可选：读取JSON文件内容并统计数量
    你可以根据JSON文件的具体结构来修改这个函数
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 根据你的JSON文件结构来统计
        # 这里提供几种常见情况的示例：

        if isinstance(data, list):
            return len(data)  # 如果是数组，返回数组长度
        elif isinstance(data, dict):
            # 如果是对象，可能需要统计某个字段
            if 'count' in data:
                return data['count']
            elif 'items' in data and isinstance(data['items'], list):
                return len(data['items'])
            else:
                return 1  # 默认返回1
        else:
            return 1

    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        return 1  # 出错时默认返回1


if __name__ == "__main__":
    # 你可以修改这些参数
    # ROOT_PATH = "."  # 根目录路径
    # OUTPUT_FILE = "statistics.json"  # 输出文件名

    scan_directories()
