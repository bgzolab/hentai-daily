import os
import re
import sys
from datetime import datetime
from datetime import timedelta

import pytest


ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from interceptor.request import MySession
from sources.bahamut import get_bahamut_article_from_author
from sources.bahamut import parse_ctime_to_timestamp


def assert_close_to(actual_timestamp, expected_datetime, tolerance_seconds=120):
    expected_timestamp = int(expected_datetime.timestamp())
    assert abs(actual_timestamp - expected_timestamp) <= tolerance_seconds


def test_parse_relative_minutes():
    before = datetime.now()
    parsed = parse_ctime_to_timestamp('15 分前')
    after = datetime.now()

    assert_close_to(parsed, before - timedelta(minutes=15))
    assert parsed <= int(after.timestamp())


def test_parse_relative_hours():
    before = datetime.now()
    parsed = parse_ctime_to_timestamp('7 小時前')

    assert_close_to(parsed, before - timedelta(hours=7))


def test_parse_yesterday_time():
    now = datetime.now()
    parsed = parse_ctime_to_timestamp('昨天 16:37')
    expected = (now - timedelta(days=1)).replace(hour=16, minute=37, second=0, microsecond=0)

    assert parsed == int(expected.timestamp())


def test_parse_day_before_yesterday_time():
    now = datetime.now()
    parsed = parse_ctime_to_timestamp('前天 08:30')
    expected = (now - timedelta(days=2)).replace(hour=8, minute=30, second=0, microsecond=0)

    assert parsed == int(expected.timestamp())


def test_parse_month_day_time():
    now = datetime.now()
    parsed = parse_ctime_to_timestamp('05-22 11:02')
    expected = datetime(now.year, 5, 22, 11, 2)
    if expected > now:
        expected = expected.replace(year=now.year - 1)

    assert parsed == int(expected.timestamp())


def test_live_bahamut_minefive5_relative_time_parsing():
    session = MySession()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh,en-US;q=0.9,en;q=0.8,zh-HK;q=0.7,zh-TW;q=0.6,zh-CN;q=0.5',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'https://home.gamer.com.tw/profile/index_creation.php?owner=minefive5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.0.0',
    }

    response = session.get(
        'https://api.gamer.com.tw/home/v2/creation_list.php?owner=minefive5&page=1&row=20',
        headers=headers,
    )

    assert response.status_code == 200

    raw_items = response.json()['data']['list']
    ctimes = [item.get('ctime', '') for item in raw_items]
    relative_pattern = re.compile(r'(?:剛剛|\d+\s*(?:分|分鐘)前|\d+\s*(?:小時|小时)前|\d+\s*天前|(?:昨天|前天)\s+\d{2}:\d{2})')

    if not any(relative_pattern.fullmatch(ctime.strip()) for ctime in ctimes if isinstance(ctime, str)):
        pytest.skip('minefive5 当前返回中没有相对时间，无法验证该分支')

    items = get_bahamut_article_from_author('minefive5')

    assert len(items) >= 10
    for item in items:
        assert item['title']
        assert item['url'].startswith('https://home.gamer.com.tw/artwork.php?sn=')
        assert isinstance(item['timestamp'], int)