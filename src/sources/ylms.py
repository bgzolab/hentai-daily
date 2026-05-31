import datetime
import html
import logging
import os
import time

import feedparser
from bs4 import BeautifulSoup

from interceptor.request import MySession


session = MySession()
logger = logging.getLogger(__name__)
thumbnail_cache = {}

YLMS_URL = "https://blog.reimu.net/"
YLMS_RSS_FALLBACK_URL = "http://reimu.bgzo.cc"
YLMS_REFERER = "https://blog.reimu.net/page/2"
YLMS_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:149.0) "
    "Gecko/20100101 Firefox/149.0"
)
YLMS_COOKIE_ENV = "YLMS_CF_CLEARANCE"
YLMS_CHALLENGE_MARKERS = (
    "cf-browser-verification",
    "Just a moment...",
    "Attention Required!",
    "challenge-platform",
)


def package_content(title, url, summary, timestamp):
    return {
        "title": title,
        "url": url,
        "summary": summary,
        "timestamp": timestamp,
    }


def get_cf_clearance():
    return os.getenv(YLMS_COOKIE_ENV, "").strip()


def build_request_headers():
    cf_clearance = get_cf_clearance()
    if not cf_clearance:
        logger.warning("YLMS cf_clearance is missing, fallback to RSS")
        return None

    return {
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,"
            "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        ),
        "Accept-Encoding": "identity",
        "Accept-Language": "zh,en-US;q=0.9,en;q=0.8,zh-HK;q=0.7,zh-TW;q=0.6,zh-CN;q=0.5",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": YLMS_REFERER,
        "User-Agent": YLMS_USER_AGENT,
        "Cookie": f"cf_clearance={cf_clearance}",
    }


def is_cloudflare_blocked(response_text):
    if not isinstance(response_text, str) or not response_text.strip():
        return False

    if (
        'article.post type-post status-publish' in response_text
        or 'class="entry-title"' in response_text
        or 'class="entry-content"' in response_text
    ):
        return False

    return any(marker in response_text for marker in YLMS_CHALLENGE_MARKERS)


def parse_ylms_timestamp(raw_value, formats=None):
    if raw_value is None:
        raise ValueError("timestamp value is required")

    if hasattr(raw_value, "tm_year"):
        return round(time.mktime(raw_value))

    if not isinstance(raw_value, str) or not raw_value.strip():
        raise ValueError("timestamp value must be a non-empty string or struct_time")

    normalized_value = raw_value.strip().replace("Z", "+00:00")

    try:
        return int(datetime.datetime.fromisoformat(normalized_value).timestamp())
    except ValueError:
        pass

    for timestamp_format in formats or ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return int(
                datetime.datetime.strptime(
                    normalized_value,
                    timestamp_format,
                ).timestamp()
            )
        except ValueError:
            continue

    raise ValueError(f"unsupported timestamp format: {raw_value}")


def parse_ylms_posts(html):
    soup = BeautifulSoup(html or "", "html.parser")
    content_list = []

    articles = soup.select("article.post.type-post.status-publish")
    for article in articles:
        title_tag = article.select_one(".entry-title a[href]")
        content_block = article.select_one(".entry-content")
        time_tag = article.select_one(
            "footer.entry-footer time.entry-date.published[datetime]"
        )

        if not title_tag or not content_block or not time_tag:
            continue

        title = title_tag.get_text(strip=True)
        article_url = title_tag.get("href", "").strip()
        published_at = time_tag.get("datetime", "").strip()

        if not title or not article_url or not published_at:
            continue

        try:
            timestamp = parse_ylms_timestamp(published_at)
        except ValueError:
            logger.warning("Skip ylms article because datetime is invalid: %s", published_at)
            continue

        thumbnail_tag = article.select_one("a.post-thumbnail img[src]")
        thumbnail_url = ""
        if thumbnail_tag:
            thumbnail_url = thumbnail_tag.get("src", "").strip()

        summary_text = content_block.get_text("", strip=True)
        if thumbnail_url:
            summary = f'<img src="{thumbnail_url}" />{summary_text}'
        else:
            summary = summary_text

        content_list.append(
            package_content(title, article_url, summary, timestamp)
        )

    return content_list


def get_entry_link(entry):
    links = getattr(entry, "links", [])
    if links:
        href = getattr(links[0], "href", "")
        if isinstance(href, str) and href.strip():
            return href.strip()

    link = getattr(entry, "link", "")
    if isinstance(link, str):
        return link.strip()

    return ""


def parse_ylms_thumbnail_from_html(response_text, article_url=""):
    soup = BeautifulSoup(response_text or "", "html.parser")

    if article_url:
        for title_tag in soup.select("article.post.type-post.status-publish .entry-title a[href]"):
            href = title_tag.get("href", "").strip()
            if href != article_url:
                continue

            article = title_tag.find_parent("article")
            if article is None:
                continue

            image_tag = article.select_one("a.post-thumbnail img[src], .entry-content img[src]")
            if image_tag is not None:
                image_url = image_tag.get("src", "").strip()
                if image_url:
                    return image_url

    image_tag = soup.select_one(
        ".post-thumbnail img[src], article.post.type-post.status-publish a.post-thumbnail img[src], .entry-content img[src]"
    )
    if image_tag is not None:
        image_url = image_tag.get("src", "").strip()
        if image_url:
            return image_url

    og_image = soup.select_one('meta[property="og:image"][content]')
    if og_image is not None:
        image_url = og_image.get("content", "").strip()
        if image_url:
            return image_url

    return ""


def get_ylms_thumbnail_for_url(article_url):
    if not article_url:
        return ""

    cached_thumbnail = thumbnail_cache.get(article_url)
    if cached_thumbnail is not None:
        return cached_thumbnail

    try:
        response = session.get(
            article_url,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": YLMS_REFERER,
                "User-Agent": YLMS_USER_AGENT,
            },
        )
        response.raise_for_status()
        thumbnail_url = parse_ylms_thumbnail_from_html(response.text, article_url)
    except Exception as error:
        logger.warning("YLMS failed to fetch thumbnail for %s: %s", article_url, error)
        thumbnail_url = ""

    thumbnail_cache[article_url] = thumbnail_url
    return thumbnail_url


def build_ylms_rss_summary(summary_html, article_url):
    soup = BeautifulSoup(summary_html or "", "html.parser")

    thumbnail_tag = soup.select_one("img[src]")
    thumbnail_url = ""
    if thumbnail_tag is not None:
        thumbnail_url = thumbnail_tag.get("src", "").strip()
        thumbnail_tag.decompose()

    for more_link in soup.select("a.more-link"):
        more_link.decompose()

    summary_text = html.unescape(soup.get_text(" ", strip=True))
    if not thumbnail_url:
        thumbnail_url = get_ylms_thumbnail_for_url(article_url)

    if thumbnail_url and summary_text:
        return f'<img src="{thumbnail_url}" />{summary_text}'

    if thumbnail_url:
        return f'<img src="{thumbnail_url}" />'

    return summary_text


def get_ylms_posts_from_rss():
    response = session.get(
        YLMS_RSS_FALLBACK_URL,
        headers={
            "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
            "Referer": YLMS_REFERER,
            "User-Agent": YLMS_USER_AGENT,
        },
    )
    response.raise_for_status()

    feed = feedparser.parse(response.text)
    content_list = []
    for entry in feed.entries:
        published_parsed = getattr(entry, "published_parsed", None)
        if published_parsed is None:
            logger.warning("Skip ylms rss entry because published_parsed is missing")
            continue

        title = getattr(getattr(entry, "title_detail", None), "value", "")
        article_url = get_entry_link(entry)
        summary_html = getattr(getattr(entry, "summary_detail", None), "value", "")

        if not title or not article_url:
            continue

        try:
            timestamp = parse_ylms_timestamp(published_parsed)
        except ValueError as error:
            logger.warning("Skip ylms rss entry because datetime is invalid: %s", error)
            continue

        content_list.append(
            package_content(
                title,
                article_url,
                build_ylms_rss_summary(summary_html, article_url),
                timestamp,
            )
        )

    logger.info("YLMS RSS fallback fetched %s posts", len(content_list))
    return content_list


def get_ylms_posts():
    headers = build_request_headers()
    if headers is None:
        return get_ylms_posts_from_rss()

    try:
        response = session.get(YLMS_URL, headers=headers)
        response.raise_for_status()
    except Exception as error:
        logger.warning("YLMS direct fetch failed, fallback to RSS: %s", error)
        return get_ylms_posts_from_rss()

    if is_cloudflare_blocked(response.text):
        logger.warning("YLMS direct fetch hit Cloudflare challenge, fallback to RSS")
        return get_ylms_posts_from_rss()

    posts = parse_ylms_posts(response.text)
    if posts:
        logger.info("YLMS direct fetch succeeded with %s posts", len(posts))
        return posts

    logger.warning("YLMS direct fetch returned no parsed posts, fallback to RSS")
    return get_ylms_posts_from_rss()