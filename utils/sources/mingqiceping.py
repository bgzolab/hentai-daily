#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author : bGZo
@Date : 2025-02-16
@Links : https://github.com/bGZo
"""
import datetime
import logging
import re
import sys

from bs4 import BeautifulSoup

from interceptor.request import MySession

session = MySession()

request_headers={
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh,en-US;q=0.9,en;q=0.8,zh-HK;q=0.7,zh-TW;q=0.6,zh-CN;q=0.5",
    "Cache-Control": "no-cache",
    "Pragma":"no-cache",
    "Referer":"https://mingqiceping.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.0.0"
}


def package_content(title, url, summary, timestamp):
    return {
        "title":    title,
        "url":      url,
        "summary":  summary,
        "timestamp":timestamp
    }


def get_mingqiceping_post(limit=10):
    content_list = []

    address_url = 'https://mingqiceping.com/wp-json/b2/v1/getPostList?post_type=post-1&post_order=new&post_row_count=4&post_count=20&post_thumb_ratio=4%2F3&post_open_type=1&post_meta%5B0%5D=title&post_meta%5B1%5D=desc&post_meta%5B2%5D=links&post_meta%5B4%5D=date&width=1300&show_widget=false&post_cat%5B0%5D=cepingzhuanqu&post_paged=1&post_i=20'
    res_json = session.post(address_url, headers=request_headers).json()
    format_data = re.sub( r'\\','', res_json.get('data'))

    soup = BeautifulSoup(format_data, 'html.parser')
    articles = soup.find_all("li", class_="post-list-item")

    for article in articles:
        title_tag = article.find("h2").find("a")

        title = title_tag.get_text(strip=True)
        article_link = title_tag["href"]
        img_tag = article.find("img", class_="post-thumb")
        image_url = img_tag.get("data-src", img_tag.get("src"))
        time = article.find("time")["datetime"]

        timestamp = \
            int(datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S").timestamp())

        content_list.append(package_content(
            title,
            article_link,
            image_url,
            timestamp
        ))
    return content_list


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    session = MySession()
    logging.info(get_mingqiceping_post())