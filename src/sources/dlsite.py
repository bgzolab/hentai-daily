import re
import datetime
import time

from bs4 import BeautifulSoup

from interceptor.request import MySession

session = MySession()

request_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh,en-US;q=0.9,en;q=0.8,zh-HK;q=0.7,zh-TW;q=0.6,zh-CN;q=0.5",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Referer": "https://www.dlsite.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.0.0"
}


def package_content(title, url, summary, timestamp):
    return {
        "title": title,
        "url": url,
        "summary": summary,
        "timestamp": timestamp
    }


def format_resize_img(work_img):
    return re.sub(
        r"(//img\.dlsite\.jp/)resize(/images2/work/doujin/RJ\d+/RJ\d+_img_main)_\d+x\d+(\.jpg)",
        r"http:\1modpub\2\3",
        work_img)


def get_dlsite_ranking_with_limit_from(html_doc, limit):
    content_list = []
    soup = BeautifulSoup(html_doc, 'html.parser')

    # 查找缩略图与描述：不要绑定到特定标签，只按 class 查找以提高鲁棒性
    works = soup.find_all(class_="work_thumb_box")
    descriptions = soup.find_all(class_="work_text")

    safe_limit = min(len(works), len(descriptions), limit)

    for i in range(safe_limit):
        work = works[i]
        description = descriptions[i]

        # 尽量兼容 <a> 或 <div> 等不同标签结构
        work_url = work.get('href') or work.find('a', href=True)['href'] if work.find('a', href=True) else None
        work_name = None
        if work.find('img') is not None:
            work_name = work.find('img').get('alt')
        else:
            # 退回到查找 title 文本
            work_name = work.get_text(strip=True)

        work_timestamp = datetime.datetime.today().timestamp()

        try:
            img_tag = work.find('img')
            work_img = img_tag.get('src') or img_tag.get('data-src')
        except Exception as e:
            work_img = None
            print("Unknown: Cannot find the image of " + (work_name or "<unknown>"))

        work_summary = ''
        if work_img:
            work_summary = '<img src ="' + format_resize_img(work_img) + '"/><br/>'

        # 如果 description 有更丰富的 HTML，提取其文本/HTML
        desc_text = ''
        try:
            desc_text = description.get_text(separator=' ', strip=True)
        except Exception:
            desc_text = ''

        work_summary += desc_text

        content_list.append(package_content(
            work_name,
            work_url,
            work_summary,
            work_timestamp
        ))
    return content_list


def get_dlsite_news_from(html_doc, limit):
    content_list = []
    soup = BeautifulSoup(html_doc, 'html.parser')

    news_list = soup.find_all("a", class_="press_item_inner")

    safe_limit = min(len(news_list), limit)

    for i in range(safe_limit):
        news = news_list[i]

        news_date = datetime.datetime.strptime(news.div.p.string, '%Y年%m月%d日')
        news_timestamp = int(time.mktime(news_date.timetuple()))
        news_tag = news.div.div.span.string
        news_title = news.find('p', class_='press_item_text').get_text(strip=True)
        news_url = news['href']

        content_list.append(package_content(
            news_title,
            news_url,
            news_tag,
            news_timestamp
        ))

    content_list.sort(key=lambda x: x['timestamp'], reverse=True)
    return content_list


def get_dlsite_game_ranking_with_limit(limit=10):
    dlsite_game = 'https://www.dlsite.com/maniax/ranking/day?category=game&sort=sale&date=30d/&lang&locale=zh_CN'
    res = session.get(dlsite_game)
    return get_dlsite_ranking_with_limit_from(res.text, limit)


def get_dlsite_comic_ranking_with_limit(limit=10):
    dlsite_comic = 'https://www.dlsite.com/maniax/ranking/day?category=comic&sort=sale&date=30d/&lang&locale=zh_CN'
    res = session.get(dlsite_comic)
    return get_dlsite_ranking_with_limit_from(res.text, limit)


def get_dlsite_voice_ranking_with_limit(limit=10):
    dlsite_voice = 'https://www.dlsite.com/maniax/ranking/day?category=voice&sort=sale&date=30d/&lang&locale=zh_CN'
    res = session.get(dlsite_voice)
    return get_dlsite_ranking_with_limit_from(res.text, limit)


def get_dlsite_news(limit=10):
    dlsite_news = 'https://info.eisys.co.jp/dlsite?locale=zh_CN'
    res = session.get(dlsite_news)
    return get_dlsite_news_from(res.text, limit)


if __name__ == '__main__':
    print(get_dlsite_voice_ranking_with_limit(10))
    # print(get_dlsite_news(10))
