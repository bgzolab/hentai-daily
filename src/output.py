import logging
import os
import re
import sys
from datetime import datetime, timedelta

import pytz
from feedgen.feed import FeedGenerator

# -------------------------Global variables Start-----------------------------
timezone = pytz.timezone('Asia/Singapore')
today = datetime.today()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


# FIXME: Does it matters?
# def get_safe_round_timestamp(timestamp):
#     now = round(get_time_from_timestamp_offset_gmt(today.timestamp()).timestamp())
#     if(now < round(timestamp)):
#         timestamp /= 1000.0
#         print('😜 Convert time to sencond.')
#     return round(timestamp)


def get_safe_utc_from_timestamp(timestamp):
    target = today
    try:
        target = datetime.utcfromtimestamp(timestamp)
    except ValueError:
        logging.info('😜 Convert time to sencond.')
        timestamp /= 1000.0
        target = datetime.utcfromtimestamp(timestamp)
    return target


def get_time_from_timestamp_offset_gmt(timestamp, gmt=8):
    return get_safe_utc_from_timestamp(timestamp) + timedelta(hours=gmt)


def output_rss_feed(entries_list, rss_feed_name):
    ## apis/feeds
    feed_directory = 'api/feeds/'

    feed_filename = feed_directory + re.sub(r' ', r'-', rss_feed_name.lower()) + '.xml'

    fg = FeedGenerator()
    fg.title(rss_feed_name + ' made by bgzo')
    fg.link(href='http://hentai.bgzo.cc', rel='alternate')
    fg.description('Just have fun, released custom rss feed.')

    for content in entries_list:
        fe = fg.add_entry()
        fe.id(content['url'])
        fe.link(href=content['url'], rel='alternate')
        fe.title(content['title'])
        fe.description(content['summary'])
        fe.pubDate(timezone.localize(get_time_from_timestamp_offset_gmt(content['timestamp'])))

    os.makedirs(os.path.dirname(feed_filename), exist_ok=True)
    fg.rss_file(feed_filename)
    logging.info("Output feeds of API successfully")


if __name__ == '__main__':
    output_rss_feed(
        [{'title': '【重要】关于DLsite comipo改版的公告',
          'url': 'https://info.eisys.co.jp/dlsite/770da7be01a55772?locale=zh_CN', 'summary': '新服务・功能',
          'timestamp': 1747756800},
         {'title': 'DLsite账号名称变更通知', 'url': 'https://info.eisys.co.jp/dlsite/f34a34bbb05320aa?locale=zh_CN',
          'summary': '公告', 'timestamp': 1744128000},
         {'title': '关于PlayDRM作品无法进行认证的现象',
          'url': 'https://info.eisys.co.jp/dlsite/59a19eb11cf6ba92?locale=zh_CN',
          'summary': '公告', 'timestamp': 1743523200},
         {'title': 'LINE Pay決済サービス終了のお知らせ',
          'url': 'https://info.eisys.co.jp/dlsite/2deea47f039d217b?locale=zh_CN', 'summary': '公告',
          'timestamp': 1743523200},
         {'title': '【重要】DLsite系统维护通知', 'url': 'https://info.eisys.co.jp/dlsite/ee5c9eaa271d3d6f?locale=zh_CN',
          'summary': '维护', 'timestamp': 1743436800},
         {'title': '商业漫画（一般·R18）卖场作品的阅览方法变更通知',
          'url': 'https://info.eisys.co.jp/dlsite/514b32eeb370b124?locale=zh_CN',
          'summary': '公告', 'timestamp': 1742832000},
         {'title': 'PayPayクレジット払いがご利用可能になりました',
          'url': 'https://info.eisys.co.jp/dlsite/b1e624408f5e7294?locale=zh_CN', 'summary': '公告',
          'timestamp': 1741536000},
         {'title': '『DLsiteアワード2024』第2回結果発表のお知らせ（大賞）',
          'url': 'https://info.eisys.co.jp/dlsite/426346d60dd1564a?locale=zh_CN',
          'summary': '公告', 'timestamp': 1741276800},
         {'title': 'DLsite用户使用条款已修订', 'url': 'https://info.eisys.co.jp/dlsite/2a54621af0071aaa?locale=zh_CN',
          'summary': '公告', 'timestamp': 1740672000},
         {'title': '『DLsiteアワード2024』第1回結果発表のお知らせ（新人賞・特別賞）',
          'url': 'https://info.eisys.co.jp/dlsite/fcef255fbdf5141e?locale=zh_CN', 'summary': '活动',
          'timestamp': 1740672000}],
        "DLSITE news"
    )
