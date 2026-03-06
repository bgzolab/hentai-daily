import re
import datetime
import time
import logging

from bs4 import BeautifulSoup

from interceptor.request import MySession

session = MySession()
logger = logging.getLogger(__name__)

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
    # 归一化：把 // 开头转成 https:
    if work_img.startswith('//'):
        work_img = 'https:' + work_img
    if work_img.startswith('http:'):
        work_img = work_img.replace('http:', 'https:', 1)
    # 将 resize 路径转换为可访问的大图 URL，并使用 https
    work_img = work_img.replace('/resize/', '/modpub/')
    work_img = re.sub(
        r'(_\d+x\d+)(\.(?:jpg|jpeg|webp|png))$',
        r'\2',
        work_img,
        flags=re.IGNORECASE
    )
    return work_img


def extract_img_url_from_text(raw_text):
    if not raw_text:
        return None
    if not isinstance(raw_text, str):
        raw_text = ' '.join(raw_text)
    raw_text = raw_text.replace('\\/', '/')
    match = re.search(
        r"(https?:)?//img\.dlsite\.jp[^\"'\s>]+?(?:jpg|jpeg|webp|png)",
        raw_text,
        flags=re.IGNORECASE
    )
    if not match:
        return None
    img_url = match.group(0)
    if img_url.startswith('//'):
        img_url = 'https:' + img_url
    if img_url.startswith('http:'):
        img_url = img_url.replace('http:', 'https:', 1)
    return img_url


def extract_img_from_tag(img_tag):
    # 优先走常见属性，再兜底扫描所有包含 src/thumb/sample 的属性。
    candidates = [
        img_tag.get('data-src'),
        img_tag.get('data-original'),
        img_tag.get('data-lazy'),
        img_tag.get('data-srcset'),
        img_tag.get('srcset'),
        img_tag.get(':src'),
        img_tag.get('v-bind:src'),
        img_tag.get('src'),
    ]
    for candidate in candidates:
        img_url = extract_img_url_from_text(candidate)
        if img_url:
            return img_url
    for attr_name, attr_val in img_tag.attrs.items():
        key = attr_name.lstrip(':').lower()
        if 'src' in key or 'thumb' in key or 'sample' in key:
            img_url = extract_img_url_from_text(attr_val)
            if img_url:
                return img_url
    return None


def extract_img_from_node_attrs(node):
    for attr_name, attr_val in node.attrs.items():
        key = attr_name.lstrip(':').lower()
        if 'src' in key or 'thumb' in key or 'sample' in key:
            img_url = extract_img_url_from_text(attr_val)
            if img_url:
                return img_url
    return None


def get_dlsite_ranking_with_limit_from(html_doc, limit):
    content_list = []
    soup = BeautifulSoup(html_doc, 'html.parser')

    # 兼容两种 DOM：先按表格行解析（若存在），不足则退回到按 class 配对解析
    content_list = []
    rows = soup.select('#ranking_table tr')
    count = 0
    if rows:
        for row in rows:
            if count >= limit:
                break
            try:
                link_tag = row.select_one('dt.work_name a') or row.select_one('a[href*="/work/"]')
                if link_tag:
                    work_url = link_tag.get('href')
                    work_name = link_tag.get_text(strip=True) or None
                else:
                    work_url = None
                    work_name = None

                img_tag = row.select_one('.work_thumb_box img')
                work_img = None
                if img_tag is not None:
                    work_img = extract_img_from_tag(img_tag)
                    if not work_name:
                        work_name = img_tag.get('alt') or img_tag.get('title') or work_name
                else:
                    work_img = None

                # 如果仍然没有图片，尝试从 data-samples / data-samples-like 属性中提取 thumb
                if not work_img:
                    for node in row.find_all(True):
                        work_img = extract_img_from_node_attrs(node)
                        if work_img:
                            break

                desc_tag = row.select_one('.work_text' )
                desc_text = ''
                if desc_tag:
                    desc_text = desc_tag.get_text(separator=' ', strip=True)

                if work_url:
                    work_url = work_url.strip()
                    if work_url.startswith('//'):
                        work_url = 'https:' + work_url
                    elif work_url.startswith('/'):
                        work_url = 'https://www.dlsite.com' + work_url
                    elif not re.match(r'^https?://', work_url):
                        work_url = 'https://www.dlsite.com/' + work_url.lstrip('./')

                if not work_url:
                    continue

                work_timestamp = int(datetime.datetime.today().timestamp())
                work_summary = ''
                # 丢弃占位 data:image，避免输出 base64 占位图
                if work_img and work_img.startswith('data:image'):
                    work_img = None
                if work_img:
                    work_summary = '<img src ="' + format_resize_img(work_img) + '"/><br/>'
                work_summary += desc_text

                content_list.append(package_content(
                    work_name,
                    work_url,
                    work_summary,
                    work_timestamp
                ))
                count += 1
            except Exception as e:
                logger.exception(f"Error parsing row: {e}")
                continue

    # 如果表格解析不能满足数量，退回到原始按 class 查找并匹配（兼容老版 DOM）
    if count < limit:
        works = soup.find_all(class_="work_thumb_box")
        descriptions = soup.find_all(class_="work_text")
        safe_limit = min(len(works), len(descriptions), limit - count)
        for i in range(safe_limit):
            work = works[i]
            description = descriptions[i]

            anchor = work.find('a', href=True)
            if anchor:
                work_url = anchor['href']
            else:
                work_url = work.get('href')

            img_tag = work.find('img')
            if img_tag is not None:
                work_name = img_tag.get('alt') or img_tag.get('title') or img_tag.get('src')
                work_img = extract_img_from_tag(img_tag)
            else:
                work_name = work.get_text(strip=True)
                work_img = None

            # 若没有图片，尝试从 work 节点的 data-samples 中提取
            if not work_img:
                # 广泛搜索当前节点及其祖先中任意包含 src/thumb/sample 的属性名
                node = work
                depth = 0
                while node is not None and depth < 4 and not work_img:
                    work_img = extract_img_from_node_attrs(node)
                    node = node.parent
                    depth += 1

            if work_url:
                work_url = work_url.strip()
                if work_url.startswith('//'):
                    work_url = 'https:' + work_url
                elif work_url.startswith('/'):
                    work_url = 'https://www.dlsite.com' + work_url
                elif not re.match(r'^https?://', work_url):
                    work_url = 'https://www.dlsite.com/' + work_url.lstrip('./')

            if not work_url:
                logger.warning(f"missing URL for work index {i}, name={(work_name or '<unknown>')}. Skipping.")
                continue

            work_timestamp = int(datetime.datetime.today().timestamp())

            work_summary = ''
            # 丢弃占位 data:image
            if work_img and work_img.startswith('data:image'):
                work_img = None
            if work_img:
                work_summary = '<img src ="' + format_resize_img(work_img) + '"/><br/>'

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
            count += 1
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
