import sys
import os
import json
import pytest

# make src importable
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from sources.dlsite import get_dlsite_ranking_with_limit_from, get_dlsite_voice_ranking_with_limit


def load_debug(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def test_game_ranking_parsing():
    html = load_debug(os.path.join(ROOT, 'debug', 'dlsite_game.html'))
    items = get_dlsite_ranking_with_limit_from(html, 10)
    # 至少返回 5 条且每条包含 title/url/timestamp
    assert len(items) >= 5
    for it in items:
        assert 'title' in it and it['title']
        assert 'url' in it and it['url'] and it['url'].startswith('http')
        assert isinstance(it['timestamp'], int)


def test_voice_ranking_parsing():
    html = load_debug(os.path.join(ROOT, 'debug', 'dlsite_voice.html'))
    items = get_dlsite_ranking_with_limit_from(html, 10)
    assert len(items) >= 3
    for it in items:
        assert it['url'].startswith('http')


def test_comic_ranking_parsing():
    html = load_debug(os.path.join(ROOT, 'debug', 'dlsite_comic.html'))
    items = get_dlsite_ranking_with_limit_from(html, 10)
    assert len(items) >= 3
    for it in items:
        assert 'title' in it
        assert it['url'].startswith('http')


def test_run_dlsite_ranking():
    # 设置代理环境变量（如果需要）
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10800'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10800'
    os.environ['ALL_PROXY'] = 'http://127.0.0.1:10800'
    result = get_dlsite_voice_ranking_with_limit(10)
    print(result)
