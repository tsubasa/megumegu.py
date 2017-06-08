# -*- coding: utf-8 -*-

from __future__ import print_function

import datetime
import hashlib
import logging
import re

import six
import requests

logger = logging.getLogger('megumegu.utils')

def filter_schedule(sites):
    site_list = []
    dt = datetime.datetime.now()

    for s in sites:
        sched = s['schedule'].split(' ')
        if len(sched) == 5 \
           and int(dt.strftime('%M')) in get_range(sched[0], 0, 59) \
           and int(dt.strftime('%H')) in get_range(sched[1], 0, 23) \
           and int(dt.strftime('%d')) in get_range(sched[2], 1, 31) \
           and int(dt.strftime('%m')) in get_range(sched[3], 1, 12) \
           and int(dt.strftime('%w')) in get_range(sched[4], 0, 6):
            site_list.append(s)
        elif len(sched) != 5:
            logger.error('SyntaxError in schedule : [%s] %s' % (s['schedule'], s.get('name', 'Unknown')))
        else:
            logger.info('Skip to schedule : [%s] %s' % (s['schedule'], s.get('name', 'Unknown')))

    return site_list

def get_range(ch, low, high, offs=1):
    opts = []
    if ',' in ch:
        for n in ch.split(','):
            opts.extend(get_range(n, low, high, offs))
    elif ch == '*':
        opts.extend(range(low, high + offs))
    else:
        if '*/' in ch:
            step = int(ch.strip('*/'))
            if low <= step and step <= high:
                opts.extend(range(low, high + offs, step))
        elif '-' in ch:
            ran = [int(n) for n in ch.split('-')]
            if ran[0] <= ran[1] \
               and low <= ran[0] and ran[0] <= high \
               and low <= ran[1] and ran[1] <= high:
                opts.extend(range(ran[0], ran[1] + offs))
        elif low <= int(ch) and int(ch) <= high:
            opts.append(int(ch))
    return opts

def merge_url(base_url, path):
    if not path:
        return base_url
    elif path.find('http') is 0:
        return path
    else:
        return requests.compat.urljoin(base_url, path)

def trim_html(html, start_tag, end_tag):
    offs_s = offs_e = None
    if start_tag:
        offs_s = html.find(start_tag)
        if offs_s == -1:
            offs_s = None
    if end_tag:
        offs_e = html.find(end_tag)
        if offs_e == -1:
            offs_e = None
        else:
            offs_e = offs_e + len(end_tag)
    return html[offs_s:offs_e]

def strip_tags(html):
    html = re.sub(r'<.*?>', '', html)  # 全てのタグを排除
    html = re.sub(r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)', r' \1 ', html)  # テキストにURLが見つかれば両サイドにスペースを挿入
    html = re.sub(r'\n?[\s|　]{2,}', '', html)  # 連続する空白を削除
    html = unescape(html.replace('\u3000', ' ').replace('\xa0', ' '))  # ユニコードの特殊文字をスペースに置換
    return unescape(html).strip()  # &amp;nbsp;などの文字列に対応するため二度実行する

def unescape(data):
    data = data.replace('&nbsp;', ' ')
    data = data.replace('&lt;', '<')
    data = data.replace('&gt;', '>')
    data = data.replace('&quot;', '"')
    return data.replace('&amp;', '&')

def enc_unicode(data):
    lookup = (
        'utf_8', 'cp932',
        'euc_jp', 'euc_jis_2004', 'euc_jisx0213',
        'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext',
        'shift_jis', 'shift_jis_2004', 'shift_jisx0213',
        'latin_1', 'ascii')
    for encoding in lookup:
        try:
            data = data.decode(encoding)
            break
        except:
            pass
    if isinstance(data, six.text_type):
        return data
    else:
        raise LookupError

def make_hash(data):
    return hashlib.md5(data.encode('unicode_escape')).hexdigest()
