import requests

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
    responses = requests.get(address).json()['data']['results']
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

