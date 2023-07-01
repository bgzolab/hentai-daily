import feedparser
import yaml
import opml
import re
import time
import datetime
import json
import os
import pytz

from feedgen.feed import FeedGenerator
from template import TEMPLATE_CONTENT_PARENT, TEMPLATE_CONTENT_CHILD, TEMPLATE_POST
from tw4gamers import get_4gamers_info_by_number
from dlsite import get_dlsite_game_ranking_with_limit
from dlsite import get_dlsite_voice_ranking_with_limit
from dlsite import get_dlsite_comic_ranking_with_limit

timezone = pytz.timezone('Asia/Singapore')
today = datetime.datetime.today()

def entry_to_dict(entry):
    timestamp = time.mktime(entry.published_parsed) # Float
    return {
        "title":        entry.title_detail.value,
        "url":          entry.links[0].href,
        "summary":      format_forum(entry.summary_detail.value),
        "timestamp":    round(timestamp) # get_safe_round_timestamp
    }

def format_forum(content):
    # www.gmgard.com
    content = re.sub(r"(static\.gmgard)(.com|.moe|.us)(\/Images\/)thumbs", r"\1\2\3upload", content)
    # www.south-plus.net
    content = re.sub(r"\[img\](.*?)p_w_picpath(.*?)\[\/img\]", r"<img src='\1\\images\2'/>", content)
    content = re.sub(r"\[img\](.*?)\[\/img\]", r"<img src='\1'/>", content)
    return content

# FIXME: Does it matters?
# def get_safe_round_timestamp(timestamp):
#     now = round(get_time_from_timestamp_offset_gmt(today.timestamp()).timestamp())
#     if(now < round(timestamp)):
#         timestamp /= 1000.0
#         print('😜 Convert time to sencond.')
#     return round(timestamp)

def get_time_from_timestamp_offset_gmt(timestamp, gmt=8):
    return get_safe_utc_from_timestamp(timestamp) + datetime.timedelta(hours=gmt)

def get_safe_utc_from_timestamp(timestamp):
    target = today
    try:
        target = datetime.datetime.utcfromtimestamp(timestamp)
    except ValueError:
        print('😜 Convert time to sencond.')
        timestamp /= 1000.0
        target = datetime.datetime.utcfromtimestamp(timestamp)
    return target


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
            contents_array = []
            feed = feedparser.parse(address)
            print("Scan " + address + " successfully. Congradulations. 🎉")
            # TODO: Add try exception of feed, such as
            # {'bozo': True, 'entries': [], 'feed': {}, 'headers': {}, 'bozo_exception': URLError(ConnectionRefusedError(111, 'Connection refused'))}
            entries = feed.entries
            for entry in entries:
                content = entry_to_dict(entry)
                try:
                    content_dict[key].append(content)
                except KeyError as e:
                    print(key + " cannot be found, so create it!😜")
                    content_dict[key]= [content]
                except Exception as e:
                    print("Unknown error" + str(e))

    return content_dict

def add_sources(content_dict, key, entries_list):
    try:
        content_dict[key] += entries_list
    except KeyError as e:
        print(key + " cannot be found, so create it!😜")
        content_dict[key]= entries_list
    return content_dict

def sort_content_dict(content_dict):
    for key in content_dict.keys():
        content_dict[key] = sorted(
            content_dict[key], 
            key = lambda i: i['timestamp'], 
            reverse=True
        )
        print("Sort the content of " + key +" successfully. Congradulations. 🎉")
    return content_dict

##########
# Output #
##########
def output_content_within_day(content_dict, start, interval_days, target_filename):
    previous_timestamp = (start - datetime.timedelta(days=interval_days)).timestamp()
    contents_with_level = ""

    for key in content_dict.keys():
        key_sorted_content =""
        
        for content in content_dict[key]:
            if(content['timestamp'] < int(previous_timestamp)):
                break
            key_sorted_content += TEMPLATE_CONTENT_CHILD.format(
                content['title'],
                content['url'],
                get_time_from_timestamp_offset_gmt(content['timestamp']).strftime('%Y%m%d %H:%M:%S'),
                content['summary']
            ) + "\n"

        contents_with_level += TEMPLATE_CONTENT_PARENT.format(
                key,
                key_sorted_content
            ) + "\n"

    title = today.strftime("%Y%m%d") + ' RSS Reader'
    updated =  today.strftime("%Y-%m-%d")
    with open(target_filename, "w") as file:
        file.write(TEMPLATE_POST.format(title, updated))
        file.write(contents_with_level)
    print("Output contents of API successfully. Congradulations. 🎉")

## apis/archives
def output_archive(rss_content_dict , archive_filename):
    os.makedirs(os.path.dirname(archive_filename), exist_ok=True)
    str_dict = json.dumps(rss_content_dict)

    with open(archive_filename, "w") as file:
        file.write(str_dict)
    print("Output archives of API successfully. Congradulations. 🎉")

## apis/feeds
def output_feed_within_day(rss_content_dict , start, interval_days, feed_directory):
    previous_timestamp = (start - datetime.timedelta(days=interval_days)).timestamp()

    for key in rss_content_dict.keys():
        feed_filename = feed_directory + re.sub(r' ', r'-', key.lower()) + '.xml'

        fg = FeedGenerator()
        fg.title(key + ' made by bGZo')
        fg.link( href='http://rss.bgzo.cc', rel='alternate')
        fg.description('Have fun )')

        for content in rss_content_dict[key]:
            if(content['timestamp'] < int(previous_timestamp)):
                break
            fe = fg.add_entry()
            fe.id(content['url'])
            fe.link(href=content['url'], rel='alternate')
            fe.title(content['title'])
            fe.description(content['summary'])
            fe.pubDate(timezone.localize(get_time_from_timestamp_offset_gmt(content['timestamp'])))
            
        os.makedirs(os.path.dirname(feed_filename), exist_ok=True)
        fg.rss_file(feed_filename)
    print("Output feeds of API successfully. Congradulations. 🎉")


if __name__ == '__main__':
    config_rss_opml = "config/rss.opml"
    target_filename =  '_posts/' + today.strftime("%Y-%m-%d") + '-' + 'daily.md'
    now = datetime.datetime.now()
    start = datetime.datetime(now.year, now.month, now.day, 5, 0, 0)
    interval_days = 1
    archive_filename = 'api/archives/' + today.strftime("%Y/%m/%d") + '.json'
    feed_directory = 'api/feeds/'

    init_rss_feed_dict( config_rss_opml )
    rss_content_dict = get_rss_content_dict()

    rss_content_dict = add_sources( 
        rss_content_dict, 
        'News',
        get_4gamers_info_by_number(9))
    rss_content_dict = add_sources(
        rss_content_dict,
        'DLsite Game Ranking',
        get_dlsite_game_ranking_with_limit(5))
    rss_content_dict = add_sources( 
        rss_content_dict,
        'DLsite Voice Ranking',
        get_dlsite_voice_ranking_with_limit(5))
    rss_content_dict = add_sources( 
        rss_content_dict,
        'DLsite Comic Ranking',
        get_dlsite_comic_ranking_with_limit(5))

    rss_content_dict = sort_content_dict(rss_content_dict)

    output_archive(rss_content_dict, archive_filename)
    output_content_within_day(rss_content_dict, start, interval_days, target_filename)
    output_feed_within_day(rss_content_dict, start, interval_days, feed_directory)