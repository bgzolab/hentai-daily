import requests

request_headers={
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh,en-US;q=0.9,en;q=0.8,zh-HK;q=0.7,zh-TW;q=0.6,zh-CN;q=0.5",
    "Cache-Control": "no-cache",
    "Pragma":"no-cache",
    "Referer":"https://www.4gamers.com.tw/gentlemen",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.0.0"
}

def package_content(title, url, summary, timestamp):
    return {
        "title":    title,
        "url":      url,
        "summary":  summary,
        "timestamp":timestamp
    }

def get_4gamers_info_by_number(number = 9):
    address = 'http://www.4gamers.com.tw/site/api/news/option-cfg/gentlemen-latest?pageSize=' + str(number)
    content_list = []
    responses = requests.get(address, request_headers).json()['data']['results']
    for response in responses:
        content_list.append(
            package_content(
                response['title'],
                response['canonicalUrl'],
                '<img src="'+response['socialBannerUrl']+'"/>\n' + response['intro'],
                response['createPublishedAt']
            )
        )
    return content_list

