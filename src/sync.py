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
from sources.llss import get_llss_post

try:
    import brotli
except ImportError:
    try:
        import brotlicffi as brotli  # type: ignore
    except ImportError:
        brotli = None

from common.strUtils import *
from output import output_rss_feed, get_time_from_timestamp_offset_gmt
from sources.bahamut import get_bahamut_article_from_author
from sources.dlsite import get_dlsite_news
from template import TEMPLATE_CONTENT_PARENT, TEMPLATE_CONTENT_CHILD, TEMPLATE_POST
from sources.mingqiceping import get_mingqiceping_post
from sources.tw4gamers import get_4gamers_info_by_number
from sources.kungal import get_kungal_posts
from sources.asmr_one import get_asmr_one_posts
from sources.nysoure import get_nysoure_posts
from sources.dlsite import get_dlsite_game_ranking_with_limit
from sources.dlsite import get_dlsite_voice_ranking_with_limit
from sources.dlsite import get_dlsite_comic_ranking_with_limit

# -------------------------Global variables Start-----------------------------
timezone = pytz.timezone('Asia/Singapore')
today = datetime.datetime.today()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
request_headers={
    "Accept": "application/json, text/plain, */*",
    # Avoid brotli in CI where br decoder may be unavailable.
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh,en-US;q=0.9,en;q=0.8,zh-HK;q=0.7,zh-TW;q=0.6,zh-CN;q=0.5",
    "Cache-Control": "no-cache",
    "Pragma":"no-cache",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:144.0) Gecko/20100101 Firefox/144.0",
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
            # request_headers['Referer'] = extract_root_url(address)
            # 模拟请求
            try:
                response = requests.get(address, headers=request_headers, timeout=30, allow_redirects=True)
            except requests.exceptions.ReadTimeout as e:
                logging.warning("Request timed out for %s: %s", address, e)
                continue
            except requests.exceptions.RequestException as e:
                logging.warning("Request failed for %s: %s", address, e)
                continue
            
            logging.info("Request %s - Status: %s, Content-Length: %s, Content-Type: %s, Content-Encoding: %s", 
                        address, response.status_code, len(response.content), 
                        response.headers.get('Content-Type', 'unknown'),
                        response.headers.get('Content-Encoding', 'none'))

            if response.status_code != 200:
                logging.error('Request %s occurs error, response code: %s', address, response.status_code)
                continue

            # 检查是否有实际内容
            if len(response.content) == 0:
                logging.warning("Response content is empty for %s", address)
                continue

            response_text = response.text
            content_encoding = response.headers.get('Content-Encoding', '').lower()

            # Some CI environments do not auto-decode Brotli responses.
            if 'br' in content_encoding:
                if brotli is None:
                    logging.warning("Brotli decoder is unavailable for %s; cannot decode br response", address)
                else:
                    try:
                        response_text = brotli.decompress(response.content).decode(response.encoding or 'utf-8', errors='replace')
                        logging.info("Manually decoded brotli response for %s", address)
                    except Exception as e:
                        logging.warning("Failed to manually decode brotli for %s: %s", address, e)

            # 使用 response_text 传递给 feedparser，确保内容已解压和解码
            content_preview = response_text[:200] if len(response_text) > 200 else response_text
            logging.info("Response preview for %s: %s...", address, content_preview)
            feed = feedparser.parse(response_text)
            entries = feed.entries
            
            # 增强调试信息
            logging.info("Scan RSS: %s with entries count: %s", address, len(entries))
            if len(entries) == 0 and feed.bozo:
                logging.warning("Feed parsing failed for %s, bozo_exception: %s", address, feed.bozo_exception)

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
    
    # 如果文件已存在，读取现有内容
    if os.path.exists(archive_filename):
        try:
            with open(archive_filename, "r") as file:
                existing_dict = json.load(file)
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Failed to read existing archive: {e}, starting fresh")
            existing_dict = {}
    else:
        existing_dict = {}

    # 解析归档日期，并计算昨天 00:00 的时间戳边界
    date_match = re.search(r"(\d{4})/(\d{2})/(\d{2})\.json$", archive_filename)
    if date_match:
        archive_date = datetime.date(
            int(date_match.group(1)),
            int(date_match.group(2)),
            int(date_match.group(3))
        )
    else:
        archive_date = datetime.date.today()

    today_start_dt = datetime.datetime.combine(archive_date, datetime.time.min)
    yesterday_start_ts = int((today_start_dt - datetime.timedelta(days=1)).timestamp())

    # 读取昨日归档（如果存在）
    yesterday_date = archive_date - datetime.timedelta(days=1)
    yesterday_filename = re.sub(
        r"\d{4}/\d{2}/\d{2}\.json$",
        yesterday_date.strftime("%Y/%m/%d") + ".json",
        archive_filename
    )
    yesterday_dict = {}
    if yesterday_filename != archive_filename and os.path.exists(yesterday_filename):
        try:
            with open(yesterday_filename, "r") as file:
                yesterday_dict = json.load(file)
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Failed to read yesterday archive: {e}, skip merge")
    
    # 合并新的内容到现有内容
    merged_dict = existing_dict.copy()
    merge_keys = {"Resources", "News"}
    ranking_keys = {
        "DLsite Game Ranking",
        "DLsite Voice Ranking",
        "DLsite Comic Ranking"
    }
    
    for key, entries in rss_content_dict.items():
        if key in merge_keys:
            # Resources/News: 在历史基础上新增，并按 URL 去重
            existing_entries = merged_dict.get(key, [])
            url_to_entry = {}

            for entry in existing_entries:
                if isinstance(entry, dict) and 'url' in entry:
                    url_to_entry[entry['url']] = entry

            for entry in entries:
                if isinstance(entry, dict) and 'url' in entry:
                    url_to_entry[entry['url']] = entry

            merged_dict[key] = list(url_to_entry.values())
        elif key in ranking_keys:
            # Ranking: 仅在抓取成功（长度=5）时覆盖；否则保留历史值
            if isinstance(entries, list) and len(entries) == 5:
                merged_dict[key] = entries
            elif key not in merged_dict:
                # 首次运行没有历史数据时，仍然写入当前结果
                merged_dict[key] = entries
            else:
                logging.warning("Skip overwrite for %s because fetched length is %s", key, len(entries) if isinstance(entries, list) else 'invalid')
        else:
            # 其他分类保持覆盖行为
            merged_dict[key] = entries

    # News/Resources 额外合并昨日归档，并舍弃前天及更早的数据
    for key in merge_keys:
        url_to_entry = {}

        yesterday_entries = yesterday_dict.get(key, [])
        if isinstance(yesterday_entries, list):
            for entry in yesterday_entries:
                if isinstance(entry, dict) and 'url' in entry:
                    url_to_entry[entry['url']] = entry

        current_entries = merged_dict.get(key, [])
        if isinstance(current_entries, list):
            for entry in current_entries:
                if isinstance(entry, dict) and 'url' in entry:
                    url_to_entry[entry['url']] = entry

        # 仅保留昨天及之后，避免前天及更早的冗余数据
        merged_dict[key] = [
            entry for entry in url_to_entry.values()
            if isinstance(entry, dict) and isinstance(entry.get('timestamp'), (int, float)) and entry['timestamp'] >= yesterday_start_ts
        ]
    
    # 仅对 Resources 和 News 按 timestamp 倒序排序，其他分类保留原顺序
    sortable_keys = {"Resources", "News"}
    for key in sortable_keys:
        entries = merged_dict.get(key)
        if isinstance(entries, list):
            merged_dict[key] = sorted(
                entries,
                key=lambda item: item.get('timestamp', 0) if isinstance(item, dict) else 0,
                reverse=True
            )

    # 强制输出顺序：先写固定分类，再追加其他分类
    preferred_order = [
        "Resources",
        "News",
        "DLsite Game Ranking",
        "DLsite Voice Ranking",
        "DLsite Comic Ranking"
    ]
    ordered_dict = {}
    for key in preferred_order:
        if key in merged_dict:
            ordered_dict[key] = merged_dict[key]
    for key, value in merged_dict.items():
        if key not in ordered_dict:
            ordered_dict[key] = value

    # 写入文件
    str_dict = json.dumps(ordered_dict)
    
    with open(archive_filename, "w") as file:
        file.write(str_dict)
    logging.info("Output archives of API successfully")


## apis/feeds
def output_feed_within_day(rss_content_dict, start, interval_days, feed_directory):
    previous_timestamp = (start - datetime.timedelta(days=interval_days)).timestamp()

    for key in rss_content_dict.keys():
        feed_filename = feed_directory + re.sub(r' ', r'-', key.lower()) + '.xml'

        fg = FeedGenerator()
        fg.title(key + ' made by bgzo')
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

# update docs/today.md and docs/zh-cn/today.md updateTime
def update_markdown_frontmatter(filepath):
    """更新 Markdown 文件的 Front Matter 中的 update 字段"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 获取当前时间，格式化为 YYYY-MM-DDTHH:MM:SS
        current_time = datetime.datetime.now(timezone).strftime('%Y-%m-%dT%H:%M:%S')
        
        # 匹配并替换 update 字段
        pattern = r'(update:\s*).+?(?=\n|$)'
        updated_content = re.sub(pattern, r'update: ' + current_time, content)
        
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        
        logging.info(f"Updated {filepath} - update time: {current_time}")
    except Exception as e:
        logging.warning(f"Failed to update {filepath}: {e}")


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

    try:
        rss_content_dict = add_sources(
            rss_content_dict,
            'News',
            get_4gamers_info_by_number(9),
            "4gamers"
        )
    except Exception as e:
        logging.warning(f"跳过4gamers: {e}")

    try:
        rss_content_dict = add_sources(
            rss_content_dict,
            'News',
            get_mingqiceping_post(),
            "mingqiceping"
        )
    except Exception as e:
        logging.warning(f"跳过mingqiceping: {e}")

    try:
        rss_content_dict = add_sources(
            rss_content_dict,
            'News',
            get_dlsite_news(DLSITE_LIMIT),
            "dlsite-news")
    except Exception as e:
        logging.warning(f"跳过dlsite-news: {e}")

    try:
        rss_content_dict = add_sources(
            rss_content_dict,
            'DLsite Game Ranking',
            get_dlsite_game_ranking_with_limit(DLSITE_LIMIT),
            None)
    except Exception as e:
        logging.warning(f"跳过DLsite Game Ranking: {e}")

    try:
        rss_content_dict = add_sources(
            rss_content_dict,
            'DLsite Voice Ranking',
            get_dlsite_voice_ranking_with_limit(DLSITE_LIMIT),
            None)
    except Exception as e:
        logging.warning(f"跳过DLsite Voice Ranking: {e}")

    try:
        rss_content_dict = add_sources(
            rss_content_dict,
            'DLsite Comic Ranking',
            get_dlsite_comic_ranking_with_limit(DLSITE_LIMIT),
            None)
    except Exception as e:
        logging.warning(f"跳过DLsite Comic Ranking: {e}")

    bahamut_author_list = ['a1102kevin']
    for author in bahamut_author_list:
        try:
            rss_content_dict = add_sources(
                rss_content_dict,
                'News',
                get_bahamut_article_from_author(author),
                "bahamut-{}".format(author))
        except Exception as e:
            logging.warning(f"跳过bahamut-{author}: {e}")

    try:
        rss_content_dict = add_sources(
            rss_content_dict,
            'Resources',
            get_asmr_one_posts(),
            "asmr-one"
        )
    except Exception as e:
        logging.warning(f"跳过asmr-one: {e}")

    try:
        rss_content_dict = add_sources(
            rss_content_dict,
            'Resources',
            get_nysoure_posts(),
            "nysoure"
        )
    except Exception as e:
        logging.warning(f"跳过nysoure: {e}")

    # try:
    #     rss_content_dict = add_sources(
    #         rss_content_dict,
    #         'Resources',
    #         get_kungal_posts(),
    #         "kungal"
    #     )
    # except Exception as e:
    #     logging.warning(f"跳过kungal: {e}")

    try:
        rss_content_dict = add_sources(
            rss_content_dict,
            'Resources',
            get_llss_post(),
            "llss"
        )
    except Exception as e:
        logging.warning(f"跳过llss: {e}")


    rss_content_dict = sort_content_dict(rss_content_dict)

    output_archive(rss_content_dict, archive_filename)
    # output_content_within_day(rss_content_dict, start, interval_days, target_filename)
    output_feed_within_day(rss_content_dict, start, interval_days, feed_directory)

    # 更新文档update时间
    update_markdown_frontmatter('docs/today.md')
    update_markdown_frontmatter('docs/zh-cn/today.md')
