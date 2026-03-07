#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author : bGZo
@Date : 2026-03-08
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
    "Accept-Encoding": "identity",
    "Accept-Language": "zh,en-US;q=0.9,en;q=0.8,zh-HK;q=0.7,zh-TW;q=0.6,zh-CN;q=0.5",
    "Cache-Control": "no-cache",
    "Pragma":"no-cache",
    "Referer":"https://www.hacg.icu/wp/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.0.0"
}


def package_content(title, url, summary, timestamp):
    return {
        "title":    title,
        "url":      url,
        "summary":  summary,
        "timestamp":timestamp
    }


def get_llss_post():
    content_list = []
    address_url = 'https://www.hacg.icu/wp/'
    response = session.get(address_url, headers=request_headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all("article", class_="status-publish")

    for article in articles:
        # WordPress uses classes like entry-title/entry-content, not tag names.
        title_tag = article.select_one(".entry-title a")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        article_link = title_tag.get("href", "")

        content_block = article.select_one(".entry-content")
        img_tag = content_block.find("img") if content_block else None
        image_url = img_tag.get("data-src") or img_tag.get("src", "") if img_tag else ""

        time_tag = article.find("time")
        if not time_tag or "datetime" not in time_tag.attrs:
            continue
        published_time = time_tag["datetime"]

        try:
            timestamp = int(datetime.datetime.strptime(
                published_time,
                "%Y-%m-%d %H:%M:%S"
            ).timestamp())
        except ValueError:
            timestamp = int(datetime.datetime.fromisoformat(
                published_time.replace("Z", "+00:00")
            ).timestamp())

        content_list.append(package_content(
            title,
            article_link,
            '<img src=\"'+image_url+'\"/>' + content_block.get_text(strip=True),
            timestamp
        ))
    return content_list


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    session = MySession()
    logging.info(get_llss_post())