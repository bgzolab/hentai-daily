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


class MySession(requests.Session):
    def send(self, request, **kwargs):
        # logging.info("Request: %s, %s, %s", request.method, request.url,request.body)
        # res = super(MySession, self).send(request, **kwargs)
        # logging.info("Response: %s", res.text)
        # return res
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
