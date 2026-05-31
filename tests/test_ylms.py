import os
import sys

import pytest


ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from sources import ylms
from sources.ylms import get_ylms_posts, parse_ylms_posts


def load_text(path):
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()


def test_parse_ylms_posts_from_local_html_sample():
    html = load_text(os.path.join(ROOT, 'docs', 'implementation-plans', 'ylms.html'))

    posts = parse_ylms_posts(html)

    assert len(posts) >= 2
    assert posts[0]['title'] == '御所动态'
    assert posts[0]['url'] == 'https://blog.reimu.net/archives/10309'
    assert posts[0]['summary'].startswith('<img src="https://blog.reimu.net/wp-content/uploads/')
    assert isinstance(posts[0]['timestamp'], int)


def test_get_ylms_posts_returns_direct_html_when_cookie_exists(monkeypatch):
    html = load_text(os.path.join(ROOT, 'docs', 'implementation-plans', 'ylms.html'))

    class DummyResponse:
        def __init__(self, text):
            self.text = text

        def raise_for_status(self):
            return None

    monkeypatch.setenv('YLMS_CF_CLEARANCE', 'dummy-cookie')
    monkeypatch.setattr(
        'sources.ylms.session.get',
        lambda url, headers=None: DummyResponse(html),
    )

    posts = get_ylms_posts()

    assert len(posts) >= 2
    assert posts[0]['url'] == 'https://blog.reimu.net/archives/10309'


def test_get_ylms_posts_falls_back_on_cloudflare_html(monkeypatch):
    rss_xml = load_text(os.path.join(ROOT, 'debug', 'ylms-rss.xml'))
    article_html = load_text(os.path.join(ROOT, 'docs', 'implementation-plans', 'ylms.html'))

    class DummyResponse:
        def __init__(self, text):
            self.text = text

        def raise_for_status(self):
            return None

    monkeypatch.setenv('YLMS_CF_CLEARANCE', 'dummy-cookie')

    def fake_get(url, headers=None):
        if url == ylms.YLMS_URL:
            return DummyResponse('Just a moment... challenge-platform')
        if url == ylms.YLMS_RSS_FALLBACK_URL:
            return DummyResponse(rss_xml)
        return DummyResponse(article_html)

    monkeypatch.setattr('sources.ylms.session.get', fake_get)

    posts = get_ylms_posts()

    assert posts[0]['title'].startswith('【R4084】')
    assert posts[0]['url'] == 'https://blog.reimu.net/archives/123807'
    assert posts[0]['summary'].startswith('<img src="https://blog.reimu.net/wp-content/uploads/')
    assert '这个周末依旧没蹲到巫女' in posts[0]['summary']


def test_get_ylms_posts_falls_back_when_direct_request_raises(monkeypatch):
    rss_xml = load_text(os.path.join(ROOT, 'debug', 'ylms-rss.xml'))
    article_html = load_text(os.path.join(ROOT, 'docs', 'implementation-plans', 'ylms.html'))

    class DummyResponse:
        def __init__(self, text):
            self.text = text

        def raise_for_status(self):
            return None

    monkeypatch.setenv('YLMS_CF_CLEARANCE', 'dummy-cookie')

    def fake_get(url, headers=None):
        if url == ylms.YLMS_URL:
            raise RuntimeError('direct failed')
        if url == ylms.YLMS_RSS_FALLBACK_URL:
            return DummyResponse(rss_xml)
        return DummyResponse(article_html)

    monkeypatch.setattr('sources.ylms.session.get', fake_get)

    posts = get_ylms_posts()

    assert len(posts) == 2
    assert posts[1]['url'] == 'https://blog.reimu.net/archives/123810'
    assert posts[1]['summary'].startswith('<img src="https://blog.reimu.net/wp-content/uploads/')
    assert '由狗叫社 ONEONE1 开发' in posts[1]['summary']


def test_get_ylms_posts_falls_back_without_cookie(monkeypatch):
    rss_xml = load_text(os.path.join(ROOT, 'debug', 'ylms-rss.xml'))
    article_html = load_text(os.path.join(ROOT, 'docs', 'implementation-plans', 'ylms.html'))

    class DummyResponse:
        def __init__(self, text):
            self.text = text

        def raise_for_status(self):
            return None

    monkeypatch.delenv('YLMS_CF_CLEARANCE', raising=False)

    def fake_get(url, headers=None):
        if url == ylms.YLMS_RSS_FALLBACK_URL:
            return DummyResponse(rss_xml)
        return DummyResponse(article_html)

    monkeypatch.setattr('sources.ylms.session.get', fake_get)

    posts = get_ylms_posts()

    assert len(posts) == 2
    assert posts[0]['title'].startswith('【R4084】')
    assert '原作是 ONEONE1 和 Kagura Games' in posts[0]['summary']


def test_get_ylms_posts_uses_embedded_rss_image_without_detail_fetch(monkeypatch):
    rss_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<rss version=\"2.0\">
  <channel>
    <item>
      <title>示例条目</title>
      <link>https://blog.reimu.net/archives/123810</link>
      <description><![CDATA[<img src=\"https://example.com/cover.jpg\" />真实摘要]]></description>
      <pubDate>Sat, 31 May 2026 10:00:00 +0800</pubDate>
    </item>
  </channel>
</rss>
"""

    class DummyResponse:
        def __init__(self, text):
            self.text = text

        def raise_for_status(self):
            return None

    monkeypatch.delenv('YLMS_CF_CLEARANCE', raising=False)

    def fake_get(url, headers=None):
        assert url == ylms.YLMS_RSS_FALLBACK_URL
        return DummyResponse(rss_xml)

    monkeypatch.setattr('sources.ylms.session.get', fake_get)

    posts = get_ylms_posts()

    assert posts == [
        {
            'title': '示例条目',
            'url': 'https://blog.reimu.net/archives/123810',
            'summary': '<img src="https://example.com/cover.jpg" />真实摘要',
            'timestamp': 1780192800 - 28800,
        }
    ]