import json
import os
import sys

import pytest


ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from sources.nysoure import (
    NYSOURE_REQUEST_HEADERS,
    build_summary,
    get_nysoure_posts,
    map_resource_entry,
    parse_release_timestamp,
)


def load_debug(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


def test_parse_release_timestamp_supports_z_suffix():
    assert parse_release_timestamp('2026-05-29T00:00:00Z') == 1780012800


def test_parse_release_timestamp_rejects_invalid_value():
    with pytest.raises(ValueError):
        parse_release_timestamp('not-a-date')


def test_build_summary_includes_image_and_escaped_title():
    payload = load_debug(os.path.join(ROOT, 'debug', 'nysoure.json'))
    summary = build_summary(payload['data'][0])
    assert summary == (
        '<img src="https://nysoure.com/api/image/19016.jpg" />'
        '<p>校园/PC/ADV</p>'
    )


def test_build_summary_falls_back_to_text_only_without_image():
    payload = load_debug(os.path.join(ROOT, 'debug', 'nysoure.json'))
    summary = build_summary(payload['data'][1])
    assert summary == '<p>喜剧/异世界</p>'


def test_map_resource_entry_returns_standard_shape():
    payload = load_debug(os.path.join(ROOT, 'debug', 'nysoure.json'))
    mapped = map_resource_entry(payload['data'][0])
    assert mapped == {
        'title': 'Relirium - レリリウム - 遺跡と出逢いと冒険と',
        'url': 'https://nysoure.com/resources/1024',
        'summary': (
            '<img src="https://nysoure.com/api/image/19016.jpg" />'
            '<p>校园/PC/ADV</p>'
        ),
        'timestamp': 1780012800,
    }


def test_map_resource_entry_skips_missing_required_fields():
    payload = load_debug(os.path.join(ROOT, 'debug', 'nysoure.json'))
    assert map_resource_entry(payload['data'][2]) is None


def test_get_nysoure_posts_from_payload(monkeypatch):
    payload = load_debug(os.path.join(ROOT, 'debug', 'nysoure.json'))

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return payload

    def fake_get(url, headers=None):
        assert url == 'https://nysoure.com/api/resource?page=1&sort=7'
        assert headers == NYSOURE_REQUEST_HEADERS
        return DummyResponse()

    monkeypatch.setattr('sources.nysoure.session.get', fake_get)

    result = get_nysoure_posts()
    assert result == [
        {
            'title': 'Relirium - レリリウム - 遺跡と出逢いと冒険と',
            'url': 'https://nysoure.com/resources/1024',
            'summary': (
                '<img src="https://nysoure.com/api/image/19016.jpg" />'
                '<p>校园/PC/ADV</p>'
            ),
            'timestamp': 1780012800,
        },
        {
            'title': '放課後カウンセリングルーム <R18>',
            'url': 'https://nysoure.com/resources/1023',
            'summary': '<p>喜剧/异世界</p>',
            'timestamp': 1780012800,
        },
    ]