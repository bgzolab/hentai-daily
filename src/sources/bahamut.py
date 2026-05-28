#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author : bGZo
@Date : 2025-06-22
@Links : https://github.com/bGZo
"""
from interceptor.request import MySession
from datetime import datetime
from datetime import timedelta
import re
import time

session = MySession()
request_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh,en-US;q=0.9,en;q=0.8,zh-HK;q=0.7,zh-TW;q=0.6,zh-CN;q=0.5",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Referer": "https://home.gamer.com.tw/profile/index_creation.php?owner={}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.0.0"
}


def package_content(title, url, summary, timestamp):
    return {
        "title": title,
        "url": url,
        "summary": summary,
        "timestamp": timestamp
    }


def parse_ctime_to_timestamp(ctime_str):
    now = datetime.now()
    current_year = now.year
    normalized_ctime = ctime_str.strip()

    if normalized_ctime == '剛剛':
        return int(now.timestamp())

    relative_minute_match = re.fullmatch(r'(\d+)\s*(?:分|分鐘)前', normalized_ctime)
    if relative_minute_match:
        return int((now - timedelta(minutes=int(relative_minute_match.group(1)))).timestamp())

    relative_hour_match = re.fullmatch(r'(\d+)\s*(?:小時|小时)前', normalized_ctime)
    if relative_hour_match:
        return int((now - timedelta(hours=int(relative_hour_match.group(1)))).timestamp())

    relative_day_match = re.fullmatch(r'(\d+)\s*天前', normalized_ctime)
    if relative_day_match:
        return int((now - timedelta(days=int(relative_day_match.group(1)))).timestamp())

    day_offset_match = re.fullmatch(r'(昨天|前天)\s+(\d{2}:\d{2})', normalized_ctime)
    if day_offset_match:
        day_offset = 1 if day_offset_match.group(1) == '昨天' else 2
        target_day = now - timedelta(days=day_offset)
        target_time = datetime.strptime(day_offset_match.group(2), "%H:%M")
        dt = target_day.replace(
            hour=target_time.hour,
            minute=target_time.minute,
            second=0,
            microsecond=0,
        )
        return int(dt.timestamp())

    # 尝试解析完整日期格式 (YYYY-MM-DD)
    try:
        dt = datetime.strptime(normalized_ctime, "%Y-%m-%d")
        return int(dt.timestamp())
    except ValueError:
        pass

    # 尝试解析省略年份的格式 (MM-DD HH:mm)
    month_day_time_match = re.fullmatch(r'(\d{2})-(\d{2})\s+(\d{2}):(\d{2})', normalized_ctime)
    if month_day_time_match:
        dt = datetime(
            current_year,
            int(month_day_time_match.group(1)),
            int(month_day_time_match.group(2)),
            int(month_day_time_match.group(3)),
            int(month_day_time_match.group(4)),
        )

        # 处理跨年问题：如果组合后日期超过当前时间，则使用前一年
        if dt > now:
            dt = dt.replace(year=current_year - 1)

        return int(dt.timestamp())

    raise ValueError(f"Unsupported ctime format: {ctime_str}")

def get_bahamut_article_from_author(author):
    content_list = []

    # https://api.gamer.com.tw/home/v2/creation_list.php?owner=a1102kevin&page=2&row=10
    address = "https://api.gamer.com.tw/home/v2/creation_list.php?owner={}&page=1&row=10".format(author)

    # 格式化同源
    request_headers['Referer'] = request_headers['Referer'].format(author)

    res_json = session.get(address, headers=request_headers)
    if res_json.status_code != 200:
        return content_list

    result = res_json.json()['data']['list']
    if len(result) == 0:
        return content_list

    for item in result:
        content_list.append(package_content(
            item["title"],
            'https://home.gamer.com.tw/artwork.php?sn={}'.format(item["csn"]),
            "<img src='{}'/>{}".format(item["coverpic"], item['content']),
            parse_ctime_to_timestamp(item['ctime']),
        ))
    return content_list

if __name__ == '__main__':
    print(get_bahamut_article_from_author('a1102kevin'))
