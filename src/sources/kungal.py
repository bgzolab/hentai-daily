import datetime
import logging
from html import escape

from interceptor.request import MySession


logger = logging.getLogger(__name__)
session = MySession()

KUNGAL_API_URL = (
    "https://www.kungal.com/api/galgame?page=1&limit=24&type=all"
    "&language=all&platform=all&sortField=time&sortOrder=desc"
)

KUNGAL_COOKIE_VALUE = (
    "{\"showKUNGalgamePageTransparency\":50,"
    "\"showKUNGalgameFontStyle\":\"system-ui\","
    "\"showKUNGalgameContentLimit\":\"nsfw\","
    "\"showKUNGalgameBackground\":0,"
    "\"showKUNGalgameBackgroundBlur\":0,"
    "\"showKUNGalgameBackgroundBrightness\":100,"
    "\"showKUNGalgameBackLoli\":false,"
    "\"showKUNGalgameSidebarCollapsed\":false}"
)

KUNGAL_REQUEST_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.kungal.com/galgame",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:149.0) "
        "Gecko/20100101 Firefox/149.0"
    ),
}


def package_content(title, url, summary, timestamp):
    return {
        "title": title,
        "url": url,
        "summary": summary,
        "timestamp": timestamp,
    }


def get_preferred_title(name_dict, galgame_id=None):
    if not isinstance(name_dict, dict):
        name_dict = {}

    for key in ("zh-cn", "zh-tw", "ja-jp", "en-us"):
        value = name_dict.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return f"KUNGal #{galgame_id}" if galgame_id is not None else "KUNGal"


def build_summary(entry):
    parts = []
    banner = entry.get("banner") if isinstance(entry, dict) else None
    if isinstance(banner, str) and banner.strip():
        parts.append(f'<img src="{escape(banner.strip(), quote=True)}" />')

    name_dict = entry.get("name") if isinstance(entry, dict) else {}
    seen_text = set()
    for key in ("zh-cn", "zh-tw", "ja-jp", "en-us"):
        value = name_dict.get(key) if isinstance(name_dict, dict) else None
        if not isinstance(value, str):
            continue
        text = value.strip()
        if not text or text in seen_text:
            continue
        seen_text.add(text)
        parts.append(f"<p>{escape(text)}</p>")

    return "".join(parts)


def parse_resource_timestamp(resource_update_time):
    if not isinstance(resource_update_time, str) or not resource_update_time.strip():
        raise ValueError("resourceUpdateTime is required")

    normalized_time = resource_update_time.strip().replace("Z", "+00:00")
    parsed_time = datetime.datetime.fromisoformat(normalized_time)
    return int(parsed_time.timestamp())


def map_galgame_entry(entry):
    if not isinstance(entry, dict):
        return None

    if entry.get("contentLimit") != "nsfw":
        return None

    galgame_id = entry.get("id")
    resource_update_time = entry.get("resourceUpdateTime")
    if galgame_id is None or resource_update_time is None:
        logger.warning("Skip KUNGal entry because id or resourceUpdateTime is missing")
        return None

    timestamp = parse_resource_timestamp(resource_update_time)
    title = get_preferred_title(entry.get("name"), galgame_id)
    url = f"https://www.kungal.com/galgame/{galgame_id}"
    summary = build_summary(entry)

    return package_content(title, url, summary, timestamp)


def get_kungal_posts(limit=24):
    request_url = KUNGAL_API_URL.replace("limit=24", f"limit={limit}", 1)
    response = session.get(
        request_url,
        headers=KUNGAL_REQUEST_HEADERS,
        cookies={"KUNGalgameSettings": KUNGAL_COOKIE_VALUE},
    )
    response.raise_for_status()

    payload = response.json()
    galgames = payload.get("galgames")
    if galgames is None:
        if payload.get("totalCount") is not None:
            logger.warning("KUNGal response contains totalCount but no galgames list")
        return []

    if not isinstance(galgames, list):
        logger.warning("KUNGal response galgames is not a list")
        return []

    content_list = []
    for galgame in galgames:
        mapped_entry = map_galgame_entry(galgame)
        if mapped_entry is not None:
            content_list.append(mapped_entry)

    logger.info("Fetched %s KUNGal NSFW entries", len(content_list))
    return content_list