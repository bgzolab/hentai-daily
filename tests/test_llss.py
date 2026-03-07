import sys
import os
import json
import pytest

# make src importable
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from sources.llss import get_llss_post

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10800'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10800'
os.environ['ALL_PROXY'] = 'http://127.0.0.1:10800'

def test_run_llss():
    result = get_llss_post()
    print(result)
