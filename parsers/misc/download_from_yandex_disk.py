#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://toster.ru/q/72866
# How to
# wget http://gist.github.com/...
# chmod +x ya.py
# ./ya.py download_url path/to/directory

import os, sys, json
import urllib.parse as ul

assert(len(sys.argv) == 3)

url = sys.argv[1]
folder = sys.argv[2]

base_url = 'https://cloud-api.yandex.net:443/v1/disk/public/resources/download?public_key='
url = ul.quote_plus(url)
res = os.popen('wget -qO - {}{}'.format(base_url, url)).read()
json_res = json.loads(res)
filename = ul.parse_qs(ul.urlparse(json_res['href']).query)['filename'][0]
os.system("wget '{}' -P '{}' -O '{}'".format(json_res['href'], folder, filename))
