import feedparser
import yaml
import opml
import re
import time
import datetime

from template import TEMPLATE_CONTENT_PARENT, TEMPLATE_CONTENT_CHILD, TEMPLATE_POST

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
        # 'NSFW'
        for address in rss_feed_dict[key]:
            contents_array = []
            feed = feedparser.parse(address)
            print("Scan " + address + " successfully! Congradulations! 🎉")
            # TODO: Add try exception of feed, such as
            # {'bozo': True, 'entries': [], 'feed': {}, 'headers': {}, 'bozo_exception': URLError(ConnectionRefusedError(111, 'Connection refused'))}
            entries = feed.entries
            for entry in entries:
                content = entry_to_dict(entry)
                try:
                    content_dict[key].append(content)
                except KeyError as e:
                    print(key + "cannot found, so create it!")
                    content_dict[key]= [content]
                except Exception as e:
                    print(e)
        # Sort for each tag
        sorted(content_dict[key], key = lambda i: i['timestamp'])
        print("Sort the content of " + key +" successfully! Congradulations! 🎉")
    return content_dict


def entry_to_dict(entry):
    timestamp = time.mktime(entry.published_parsed)

    return {
        "title":        entry.title_detail.value,
        "url":          entry.links[0].href,
        "summary":      format_forum(entry.summary_detail.value),
        "publish_date": entry.published,
        "timestamp": round(timestamp)
    }


def format_forum(content):
    # www.gmgard.com
    content = re.sub(r"(static\.gmgard)(.com|.moe|.us)(\/Images\/)thumbs", r"\1\2\3upload", content)

    # www.south-plus.net
    content = re.sub(r"\[img\](.*?)p_w_picpath(.*?)\[\/img\]", r"<img src='\1\\images\2'/>", content)
    content = re.sub(r"\[img\](.*?)\[\/img\]", r"<img src='\1'/>", content)
    return content


def output_content_within_day(content_dict, day, target_filename):
    previous_timestamp = (datetime.datetime.today() - datetime.timedelta(days=day)).timestamp()
    contents_with_level = ""

    for key in content_dict.keys():
        key_sorted_content =""
        
        for content in content_dict[key]:
            if(content['timestamp'] < int(previous_timestamp)):
                break
            key_sorted_content += TEMPLATE_CONTENT_CHILD.format(
                content['title'],
                content['url'],
                datetime.datetime.utcfromtimestamp(content['timestamp']).strftime('%Y%m%d %H:%M:%S'),
                content['summary']
            ) + "\n"

        contents_with_level += TEMPLATE_CONTENT_PARENT.format(
                key,
                key_sorted_content
            ) + "\n"

    title = datetime.datetime.today().strftime("%Y%m%d") + ' RSS Reader'
    updated =  datetime.datetime.today().strftime("%Y-%m-%d")
    with open(target_filename, "w") as file:
        file.write(TEMPLATE_POST.format(title, updated))
        file.write(contents_with_level)


if __name__ == '__main__':
    config_rss_opml = "config/rss.opml"
    target_filename =  '_posts/' \
        + datetime.datetime.today().strftime("%Y-%m-%d") + '-' + 'daily.md'
    interval_day = 2

    init_rss_feed_dict( config_rss_opml )
    output_content_within_day(get_rss_content_dict(), interval_day, target_filename)
