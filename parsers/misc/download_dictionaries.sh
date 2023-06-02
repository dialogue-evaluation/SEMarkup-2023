#!/usr/bin/env bash

# Compreno
./download_from_yandex_disk.py https://disk.yandex.ru/d/hlQ77INmJzxVdg .
unrar x MorphoDic_full_utf8.rar MorphoDic_OUT.txt
mv MorphoDic_OUT.txt ComprenoFull.txt
rm MorphoDic_full_utf8.rar

# Zaliznyak
./download_from_yandex_disk.py https://disk.yandex.ru/d/Q8tM7IwEQafyY .
unzip dict_zaliz_utf8.zip
cat dict/* > Zaliz.txt
rm -rf dict/ dict_zaliz_utf8.zip

