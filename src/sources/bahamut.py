#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author : bGZo
@Date : 2025-06-22
@Links : https://github.com/bGZo
"""
from interceptor.request import MySession
from datetime import datetime
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

    # 尝试解析完整日期格式 (YYYY-MM-DD)
    try:
        dt = datetime.strptime(ctime_str, "%Y-%m-%d")
        return int(dt.timestamp())
    except ValueError:
        pass

    # 尝试解析省略年份的格式 (MM-DD HH:mm)
    try:
        # 解析月、日、时、分
        dt_no_year = datetime.strptime(ctime_str, "%m-%d %H:%M")
        # 组合当前年份
        dt = dt_no_year.replace(year=current_year)

        # 处理跨年问题：如果组合后日期超过当前时间，则使用前一年
        if dt > now:
            dt = dt.replace(year=current_year - 1)

        return int(dt.timestamp())
    except ValueError:
        pass

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
