import sys

import feedparser
import opml
import re
import time
import datetime
import json
import os
import pytz
import logging

import requests
from feedgen.feed import FeedGenerator

from common.strUtils import *
from output import output_rss_feed, get_time_from_timestamp_offset_gmt
from sources.bahamut import get_bahamut_article_from_author
from sources.dlsite import get_dlsite_news
from template import TEMPLATE_CONTENT_PARENT, TEMPLATE_CONTENT_CHILD, TEMPLATE_POST
from sources.mingqiceping import get_mingqiceping_post
from sources.tw4gamers import get_4gamers_info_by_number
from sources.dlsite import get_dlsite_game_ranking_with_limit
from sources.dlsite import get_dlsite_voice_ranking_with_limit
from sources.dlsite import get_dlsite_comic_ranking_with_limit

# -------------------------Global variables Start-----------------------------
timezone = pytz.timezone('Asia/Singapore')
today = datetime.datetime.today()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
request_headers={
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh,en-US;q=0.9,en;q=0.8,zh-HK;q=0.7,zh-TW;q=0.6,zh-CN;q=0.5",
    "Cache-Control": "no-cache",
    "Pragma":"no-cache",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.0.0",
    "Referer": "",
}


# -------------------------Global variables End-----------------------------


def entry_to_dict(entry):
    timestamp = time.mktime(entry.published_parsed)  # Float
    return {
        "title": entry.title_detail.value,
        "url": entry.links[0].href,
        "summary": format_forum(entry.summary_detail.value),
        "timestamp": round(timestamp)  # get_safe_round_timestamp
    }


def format_forum(content):
    # www.gmgard.com
    content = re.sub(r"(static\.gmgard)(.com|.moe|.us)(\/Images\/)thumbs", r"\1\2\3upload", content)
    # www.south-plus.net
    content = re.sub(r"\[img\](.*?)p_w_picpath(.*?)\[\/img\]", r"<img src='\1\\images\2'/>", content)
    content = re.sub(r"\[img\](.*?)\[\/img\]", r"<img src='\1'/>", content)
    return content


################
# Main Process #
################
rss_feed_dict = {}


def init_rss_feed_dict(config_rss_opml):
    # Init to get the feed to rss_feed_dict and 
    # RSS Feed
    with open(config_rss_opml, "r") as file:
        data_rss = opml.parse(file)
    for outlines in data_rss:
        dict_id = outlines.title
        rss_list = []
        for outline in outlines:
            rss_list.append(outline.xmlUrl)
        rss_feed_dict[dict_id] = rss_list


def get_rss_content_dict():
    content_dict = {}

    for key in rss_feed_dict.keys():
        for address in rss_feed_dict[key]:
            # 设置同源
            request_headers['Referer'] = extract_root_url(address)
            # 模拟请求
            response = requests.get(address, headers=request_headers)
            if response.status_code != 200:
                logging.error('Request %s occurs error, response code: %s', address, response.status_code)
                continue

            feed = feedparser.parse(response.content)
            entries = feed.entries
            logging.info("Scan RSS: %s with entries: %s", address, entries)

            for entry in entries:
                content = entry_to_dict(entry)
                try:
                    content_dict[key].append(content)
                except KeyError as e:
                    # key cannot be found, so init it
                    content_dict[key] = [content]
                except Exception as e:
                    logging.info("Unknown error" + str(e))

    return content_dict


def add_sources(content_dict, key, entries_list, rss_feed_name):
    try:
        content_dict[key] += entries_list
        if rss_feed_name is not None:
            output_rss_feed(entries_list, rss_feed_name)
    except KeyError as e:
        logging.info(key + " cannot be found, so create it!😜")
        content_dict[key] = entries_list
    return content_dict


def sort_content_dict(content_dict):
    for key in content_dict.keys():
        content_dict[key] = sorted(
            content_dict[key],
            key=lambda i: i['timestamp'],
            reverse=True
        )
        logging.info("Sort the content of " + key)
    return content_dict


##########
# Output #
##########
def output_content_within_day(content_dict, start, interval_days, target_filename):
    previous_timestamp = (start - datetime.timedelta(days=interval_days)).timestamp()
    contents_with_level = ""

    for key in content_dict.keys():
        key_sorted_content = ""
        key_sorted_content_index = 0

        for content in content_dict[key]:
            if content['timestamp'] < int(previous_timestamp):
                break
            key_sorted_content += TEMPLATE_CONTENT_CHILD.format(
                content['title'],
                content['url'],
                get_time_from_timestamp_offset_gmt(content['timestamp']).strftime('%Y%m%d %H:%M:%S'),
                content['summary']
            ) + "\n"
            key_sorted_content_index += 1

        if key_sorted_content != "":
            contents_with_level += TEMPLATE_CONTENT_PARENT.format(
                key + '(' + str(key_sorted_content_index) + ')',
                key_sorted_content
            ) + "\n"

    title = today.strftime("%Y%m%d") + ' Hentai Reader'
    updated = today.strftime("%Y-%m-%d")
    with open(target_filename, "w") as file:
        file.write(TEMPLATE_POST.format(title, updated))
        file.write(contents_with_level)
    logging.info("Output contents of API")


## apis/archives
def output_archive(rss_content_dict, archive_filename):
    os.makedirs(os.path.dirname(archive_filename), exist_ok=True)
    str_dict = json.dumps(rss_content_dict)

    with open(archive_filename, "w") as file:
        file.write(str_dict)
    logging.info("Output archives of API successfully")


## apis/feeds
def output_feed_within_day(rss_content_dict, start, interval_days, feed_directory):
    previous_timestamp = (start - datetime.timedelta(days=interval_days)).timestamp()

    for key in rss_content_dict.keys():
        feed_filename = feed_directory + re.sub(r' ', r'-', key.lower()) + '.xml'

        fg = FeedGenerator()
        fg.title(key + ' made by bGZo')
        fg.link(href='http://hentai.bgzo.cc', rel='alternate')
        fg.description('Have fun )')

        for content in rss_content_dict[key]:
            if (content['timestamp'] < int(previous_timestamp)):
                break
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
    config_rss_opml = "config/rss.opml"
    # target_filename = '_posts/' + today.strftime("%Y-%m-%d") + '-' + 'daily.md'
    archive_filename = 'api/archives/' + today.strftime("%Y/%m/%d") + '.json'
    feed_directory = 'api/feeds/'
    DLSITE_LIMIT = 5

    now = datetime.datetime.now()
    start = datetime.datetime(now.year, now.month, now.day, 5, 0, 0)
    interval_days = 1

    init_rss_feed_dict(config_rss_opml)
    rss_content_dict = get_rss_content_dict()

    rss_content_dict = add_sources(
        rss_content_dict,
        'News',
        get_4gamers_info_by_number(9),
        "4gamers"
    )

    rss_content_dict = add_sources(
        rss_content_dict,
        'News',
        get_mingqiceping_post(),
        "mingqiceping"
    )

    rss_content_dict = add_sources(
        rss_content_dict,
        'News',
        get_dlsite_news(DLSITE_LIMIT),
        "dlsite-news")

    rss_content_dict = add_sources(
        rss_content_dict,
        'DLsite Game Ranking',
        get_dlsite_game_ranking_with_limit(DLSITE_LIMIT),
        None)

    rss_content_dict = add_sources(
        rss_content_dict,
        'DLsite Voice Ranking',
        get_dlsite_voice_ranking_with_limit(DLSITE_LIMIT),
        None)

    rss_content_dict = add_sources(
        rss_content_dict,
        'DLsite Comic Ranking',
        get_dlsite_comic_ranking_with_limit(DLSITE_LIMIT),
        None)

    bahamut_author_list = ['a1102kevin']
    for author in bahamut_author_list:
        rss_content_dict = add_sources(
            rss_content_dict,
            'News',
            get_bahamut_article_from_author(author),
            "bahamut-{}".format(author))

    rss_content_dict = sort_content_dict(rss_content_dict)

    output_archive(rss_content_dict, archive_filename)
    # output_content_within_day(rss_content_dict, start, interval_days, target_filename)
    output_feed_within_day(rss_content_dict, start, interval_days, feed_directory)
