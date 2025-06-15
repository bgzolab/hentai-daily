#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author : bGZo
@Date : 2025-06-15
@Links : https://github.com/bGZo
"""
from urllib.parse import urlparse

def extract_root_url(url):
    """
    提取URL的根网址
    Args:
        url (str): 完整的URL地址
    Returns:
        str: 根网址 (协议 + 域名)
    Examples:
        >>> extract_root_url("https://www.example.com/path/to/page?param=value")
        'https://www.example.com'

        >>> extract_root_url("http://subdomain.site.org:8080/api/data")
        'http://subdomain.site.org:8080'

        >>> extract_root_url("ftp://files.example.com/folder/file.txt")
        'ftp://files.example.com'
    """
    try:
        # 如果URL没有协议，默认添加http://
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'http://' + url

        parsed = urlparse(url)

        # 构建根网址：协议 + ://+ 域名 + 端口(如果有)
        root_url = f"{parsed.scheme}://{parsed.netloc}"

        return root_url

    except Exception as e:
        raise ValueError(f"无效的URL: {url}, 错误: {str(e)}")


# 测试用例
if __name__ == "__main__":
    test_urls = [
        "https://www.example.com/path/to/page?param=value#section",
        "http://subdomain.site.org:8080/api/data",
        "https://github.com/user/repo/blob/main/file.py",
        "ftp://files.example.com/folder/file.txt",
        "www.google.com/search?q=python",  # 没有协议的URL
        "https://localhost:3000/dashboard",
        "http://192.168.1.1:8080/admin",
    ]

    for url in test_urls:
        try:
            root = extract_root_url(url)
            print(f"原URL: {url}")
            print(f"根网址: {root}")
            print("-" * 50)
        except ValueError as e:
            print(f"错误: {e}")
            print("-" * 50)