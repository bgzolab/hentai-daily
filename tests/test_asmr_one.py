import json
import os
import sys

import pytest


ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from sources.asmr_one import (
    ASMR_ONE_REQUEST_HEADERS,
    build_summary,
    get_asmr_one_posts,
    map_work_entry,
    parse_create_date_timestamp,
)


def load_debug(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


def test_parse_create_date_timestamp_supports_date_only_string():
    assert parse_create_date_timestamp('2026-05-29') == 1780012800


def test_parse_create_date_timestamp_rejects_invalid_value():
    with pytest.raises(ValueError):
        parse_create_date_timestamp('2026/05/29')


def test_build_summary_includes_cover_and_text_parts():
    payload = load_debug(os.path.join(ROOT, 'debug', 'asmr_one.json'))
    summary = build_summary(payload['works'][0])
    assert summary == (
        '<img src="https://api.asmr-200.com/api/cover/1576433.jpg?type=main" />'
        '<p>J〇ほんぽ/秋山はるる/A &amp; B</p>'
    )


def test_build_summary_keeps_image_only_when_text_is_missing():
    payload = load_debug(os.path.join(ROOT, 'debug', 'asmr_one.json'))
    summary = build_summary(payload['works'][3])
    assert summary == '<img src="https://api.asmr-200.com/api/cover/1575100.jpg?type=main" />'


def test_map_work_entry_returns_standard_shape():
    payload = load_debug(os.path.join(ROOT, 'debug', 'asmr_one.json'))
    mapped = map_work_entry(payload['works'][0])
    assert mapped == {
        'title': '✅ドスケベ差分付き✅【全編ぐっぽり両耳奥舐め】お耳がバグるまで出られない忍びの森',
        'url': 'https://www.asmr.one/work/RJ01576433',
        'summary': (
            '<img src="https://api.asmr-200.com/api/cover/1576433.jpg?type=main" />'
            '<p>J〇ほんぽ/秋山はるる/A &amp; B</p>'
        ),
        'timestamp': 1780012800,
    }


def test_map_work_entry_skips_invalid_or_non_nsfw_entries():
    payload = load_debug(os.path.join(ROOT, 'debug', 'asmr_one.json'))
    assert map_work_entry(payload['works'][1]) is None
    assert map_work_entry(payload['works'][2]) is None


def test_get_asmr_one_posts_from_payload(monkeypatch):
    payload = load_debug(os.path.join(ROOT, 'debug', 'asmr_one.json'))

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return payload

    def fake_get(url, headers=None):
        assert url == 'https://api.asmr-200.com/api/works?order=create_date&sort=desc&page=1&pageSize=20&subtitle=0'
        assert headers == ASMR_ONE_REQUEST_HEADERS
        return DummyResponse()

    monkeypatch.setattr('sources.asmr_one.session.get', fake_get)

    result = get_asmr_one_posts()
    assert result == [
        {
            'title': '✅ドスケベ差分付き✅【全編ぐっぽり両耳奥舐め】お耳がバグるまで出られない忍びの森',
            'url': 'https://www.asmr.one/work/RJ01576433',
            'summary': (
                '<img src="https://api.asmr-200.com/api/cover/1576433.jpg?type=main" />'
                '<p>J〇ほんぽ/秋山はるる/A &amp; B</p>'
            ),
            'timestamp': 1780012800,
        },
        {
            'title': 'Image only sample',
            'url': 'https://www.asmr.one/work/RJ01575100',
            'summary': '<img src="https://api.asmr-200.com/api/cover/1575100.jpg?type=main" />',
            'timestamp': 1780012800,
        },
    ]