import datetime
import logging
from html import escape

from interceptor.request import MySession


logger = logging.getLogger(__name__)
session = MySession()

NYSOURE_API_URL = "https://nysoure.com/api/resource?page=1&sort=7"

NYSOURE_REQUEST_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://nysoure.com/?sort=7",
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


def parse_release_timestamp(release_date):
    if not isinstance(release_date, str) or not release_date.strip():
        raise ValueError("release_date is required")

    normalized_time = release_date.strip().replace("Z", "+00:00")

    try:
        parsed_time = datetime.datetime.fromisoformat(normalized_time)
    except ValueError as error:
        raise ValueError("release_date must be a valid ISO 8601 string") from error

    return int(parsed_time.timestamp())


def build_summary(entry):
    if not isinstance(entry, dict):
        entry = {}

    title = entry.get("title")
    title_text = title.strip() if isinstance(title, str) else ""
    escaped_title = escape(title_text)
    summary_parts = []

    image = entry.get("image")
    image_id = image.get("id") if isinstance(image, dict) else None
    if image_id is not None:
        summary_parts.append(
            f'<img src="https://nysoure.com/api/image/{image_id}.jpg" />'
        )
    else:
        logger.warning("Build nysoure summary without image id")

    summary_parts.append(f"<p>{escaped_title}</p>")
    return "".join(summary_parts)


def map_resource_entry(entry):
    if not isinstance(entry, dict):
        logger.warning("Skip nysoure entry because payload is not a dict")
        return None

    resource_id = entry.get("id")
    title = entry.get("title")
    release_date = entry.get("release_date")

    if resource_id is None:
        logger.warning("Skip nysoure entry because id is missing")
        return None

    if not isinstance(title, str) or not title.strip():
        logger.warning("Skip nysoure entry %s because title is missing", resource_id)
        return None

    if not isinstance(release_date, str) or not release_date.strip():
        logger.warning(
            "Skip nysoure entry %s because release_date is missing",
            resource_id,
        )
        return None

    timestamp = parse_release_timestamp(release_date)
    return package_content(
        title.strip(),
        f"https://nysoure.com/resources/{resource_id}",
        build_summary(entry),
        timestamp,
    )


def get_nysoure_posts(page=1, sort=7):
    request_url = f"https://nysoure.com/api/resource?page={page}&sort={sort}"
    response = session.get(request_url, headers=NYSOURE_REQUEST_HEADERS)
    response.raise_for_status()

    payload = response.json()
    resources = payload.get("data") if isinstance(payload, dict) else None
    if resources is None:
        logger.warning("Nysoure response does not contain data list")
        return []

    if not isinstance(resources, list):
        logger.warning("Nysoure response data is not a list")
        return []

    content_list = []
    for resource in resources:
        try:
            mapped_resource = map_resource_entry(resource)
        except ValueError as error:
            logger.warning("Skip nysoure entry because timestamp is invalid: %s", error)
            continue

        if mapped_resource is not None:
            content_list.append(mapped_resource)

    logger.info("Fetched %s nysoure entries", len(content_list))
    return content_list