#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author : bGZo
@Date : 2025-02-15
@Links : https://github.com/bGZo
"""
import logging
import sys

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class MySession(requests.Session):
    def __init__(self, retries=3, backoff_factor=0.5, timeout=5):
        super(MySession, self).__init__()

        # 配置重试策略
        retry_strategy = Retry(
            total=retries,                          # 总共重试次数
            backoff_factor=backoff_factor,          # 退避时间因子（指数退避）
            status_forcelist=[500, 502, 503, 504],  # 针对这些错误状态码重试
            allowed_methods=["GET", "POST"],        # 只对 GET/POST 请求重试
            raise_on_status=False,                  # 避免直接抛出异常

        )

        # 给所有 HTTP 请求应用重试策略
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.mount("http://", adapter)
        self.mount("https://", adapter)

        self.timeout = timeout  # 超时时间

    def send(self, request, **kwargs):
        # logging.info("Request: %s, %s, %s", request.method, request.url,request.body)
        # res = super(MySession, self).send(request, **kwargs)
        # logging.info("Response: %s", res.text)
        # return res
        kwargs.setdefault("timeout", self.timeout)  # 设置默认超时时间
        body = request.body if request.body is not None else "<empty>"
        logging.info("Request: %s, %s, %s", request.method, request.url, body)

        res = super(MySession, self).send(request, **kwargs)

        content_type = res.headers.get("Content-Type", "")
        if "text/html" in content_type:
            response_text = res.text.replace("\n", " ").replace("\r", " ")
            logging.info("Response: %s", response_text)
        else:
            logging.info("Response: %s", res.text)

        return res

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)  # 设置最低日志级别
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    session = MySession()
    response = session.get("https://www.baidu.com/")

    session = MySession(retries=3, backoff_factor=1, timeout=5)

    try:
        response = session.get("https://www.baidu111.com/")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed after retries: {e}")