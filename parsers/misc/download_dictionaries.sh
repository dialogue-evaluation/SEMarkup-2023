#!/usr/bin/env bash

# Download Compreno
./download_from_yandex_disk.py https://disk.yandex.ru/d/hlQ77INmJzxVdg .
unrar x MorphoDic_full_utf8.rar MorphoDic_OUT.txt
mv MorphoDic_OUT.txt Compreno.txt
rm MorphoDic_full_utf8.rar

# Download Zaliznyak
./download_from_yandex_disk.py https://disk.yandex.ru/d/Q8tM7IwEQafyY .
unzip dict_zaliz_utf8.zip
cat dict/* > Zaliz.txt
rm -rf dict/ dict_zaliz_utf8.zip

# Move dictionaries to parsers/dicts directory
mkdir ../dicts
mv Compreno.txt Zaliz.txt ../dicts/
