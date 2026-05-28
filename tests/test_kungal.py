import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from sources.kungal import build_summary, get_kungal_posts, get_preferred_title, map_galgame_entry


def load_debug(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


def test_get_preferred_title_priority():
    payload = load_debug(os.path.join(ROOT, 'debug', 'kungal.json'))
    assert get_preferred_title(payload['galgames'][0]['name'], 6141) == '茜のちいさな花びら'
    assert get_preferred_title(payload['galgames'][2]['name'], 6001) == 'Only English Title'
    assert get_preferred_title({'zh-cn': '', 'zh-tw': '', 'ja-jp': '', 'en-us': ''}, 9999) == 'KUNGal #9999'


def test_build_summary_filters_empty_translations():
    summary = build_summary({
        'banner': 'https://image.kungal.com/galgame/7000/banner/banner.webp',
        'name': {
            'zh-cn': '中文标题',
            'zh-tw': '',
            'ja-jp': '日本語タイトル',
            'en-us': 'English Title',
        },
    })
    assert summary.startswith('<img src="https://image.kungal.com/galgame/7000/banner/banner.webp" />')
    assert '<p>中文标题</p>' in summary
    assert '<p>日本語タイトル</p>' in summary
    assert '<p>English Title</p>' in summary
    assert '<p></p>' not in summary
    assert summary.index('<p>中文标题</p>') < summary.index('<p>日本語タイトル</p>')
    assert summary.index('<p>日本語タイトル</p>') < summary.index('<p>English Title</p>')


def test_map_galgame_entry_only_accepts_nsfw():
    payload = load_debug(os.path.join(ROOT, 'debug', 'kungal.json'))
    assert map_galgame_entry(payload['galgames'][0]) is None

    mapped = map_galgame_entry(payload['galgames'][1])
    assert mapped is not None
    assert mapped['title'] == '催眠施術病院の美巨乳補完プログラム'
    assert mapped['url'] == 'https://www.kungal.com/galgame/5983'
    assert mapped['summary'].startswith('<img src="https://image.kungal.com/galgame/5983/banner/banner.webp" />')
    assert isinstance(mapped['timestamp'], int)


def test_get_kungal_posts_from_payload(monkeypatch):
    payload = load_debug(os.path.join(ROOT, 'debug', 'kungal.json'))

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return payload

    def fake_get(url, headers=None, cookies=None):
        assert 'limit=24' in url
        assert headers is not None
        assert cookies is not None
        assert 'KUNGalgameSettings' in cookies
        return DummyResponse()

    monkeypatch.setattr('sources.kungal.session.get', fake_get)

    result = get_kungal_posts()
    assert [item['url'] for item in result] == [
        'https://www.kungal.com/galgame/5983',
        'https://www.kungal.com/galgame/6001',
    ]