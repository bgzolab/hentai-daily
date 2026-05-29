import datetime
import logging
from html import escape

from interceptor.request import MySession


logger = logging.getLogger(__name__)
session = MySession()

ASMR_ONE_API_URL = (
    "https://api.asmr-200.com/api/works?order=create_date&sort=desc"
    "&page=1&pageSize=20&subtitle=0"
)

ASMR_ONE_REQUEST_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.asmr.one/",
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


def parse_create_date_timestamp(create_date):
    if not isinstance(create_date, str) or not create_date.strip():
        raise ValueError("create_date is required")

    try:
        parsed_date = datetime.date.fromisoformat(create_date.strip())
    except ValueError as error:
        raise ValueError("create_date must be a valid YYYY-MM-DD string") from error

    # Date-only feeds align to the archive boundary by treating the day as UTC 00:00.
    parsed_datetime = datetime.datetime.combine(
        parsed_date,
        datetime.time.min,
        tzinfo=datetime.timezone.utc,
    )
    return int(parsed_datetime.timestamp())


def get_tag_names(entry):
    tags = entry.get("tags") if isinstance(entry, dict) else None
    if not isinstance(tags, list):
        return []

    tag_names = []
    for tag in tags:
        if not isinstance(tag, dict):
            continue
        name = tag.get("name")
        if not isinstance(name, str):
            i18n = tag.get("i18n")
            zh_cn = i18n.get("zh-cn") if isinstance(i18n, dict) else None
            name = zh_cn.get("name") if isinstance(zh_cn, dict) else None
        if not isinstance(name, str):
            continue
        text = name.strip()
        if text:
            tag_names.append(text)

    return tag_names


def build_summary(entry):
    if not isinstance(entry, dict):
        entry = {}

    summary_parts = []

    main_cover_url = entry.get("mainCoverUrl")
    if isinstance(main_cover_url, str) and main_cover_url.strip():
        summary_parts.append(f'<img src="{escape(main_cover_url.strip(), quote=True)}" />')
    else:
        logger.warning("Build ASMR.one summary without mainCoverUrl")

    name = entry.get("name")
    text_parts = []
    if isinstance(name, str) and name.strip():
        text_parts.append(name.strip())

    vas = entry.get("vas")
    if isinstance(vas, list):
        for voice_actor in vas:
            if not isinstance(voice_actor, dict):
                continue
            vas_name = voice_actor.get("name")
            if isinstance(vas_name, str) and vas_name.strip():
                text_parts.append(vas_name.strip())

    if text_parts:
        escaped_text = escape("/".join(text_parts))
        summary_parts.append(f"<p>{escaped_text}</p>")

    tag_names = get_tag_names(entry)
    if tag_names:
        summary_parts.append(f"<p>{escape('/'.join(tag_names))}</p>")

    return "".join(summary_parts)


def map_work_entry(entry):
    if not isinstance(entry, dict):
        logger.warning("Skip ASMR.one entry because payload is not a dict")
        return None

    work_id = entry.get("id")
    if entry.get("nsfw") is not True:
        logger.warning("Skip ASMR.one entry %s because nsfw is not true", work_id)
        return None

    title = entry.get("title")
    source_id = entry.get("source_id")
    create_date = entry.get("create_date")
    main_cover_url = entry.get("mainCoverUrl")

    if not isinstance(title, str) or not title.strip():
        logger.warning("Skip ASMR.one entry %s because title is missing", work_id)
        return None

    if not isinstance(source_id, str) or not source_id.strip():
        logger.warning("Skip ASMR.one entry %s because source_id is missing", work_id)
        return None

    if not isinstance(create_date, str) or not create_date.strip():
        logger.warning("Skip ASMR.one entry %s because create_date is missing", work_id)
        return None

    if not isinstance(main_cover_url, str) or not main_cover_url.strip():
        logger.warning("Skip ASMR.one entry %s because mainCoverUrl is missing", work_id)
        return None

    timestamp = parse_create_date_timestamp(create_date)
    return package_content(
        title.strip(),
        f"https://www.asmr.one/work/{source_id.strip()}",
        build_summary(entry),
        timestamp,
    )


def get_asmr_one_posts(page=1, page_size=20):
    request_url = (
        "https://api.asmr-200.com/api/works?order=create_date&sort=desc"
        f"&page={page}&pageSize={page_size}&subtitle=0"
    )
    response = session.get(request_url, headers=ASMR_ONE_REQUEST_HEADERS)
    response.raise_for_status()

    payload = response.json()
    works = payload.get("works") if isinstance(payload, dict) else None
    if works is None:
        logger.warning("ASMR.one response does not contain works list")
        return []

    if not isinstance(works, list):
        logger.warning("ASMR.one response works is not a list")
        return []

    content_list = []
    for work in works:
        try:
            mapped_work = map_work_entry(work)
        except ValueError as error:
            logger.warning("Skip ASMR.one entry because date is invalid: %s", error)
            continue

        if mapped_work is not None:
            content_list.append(mapped_work)

    logger.info("Fetched %s ASMR.one entries", len(content_list))
    return content_list