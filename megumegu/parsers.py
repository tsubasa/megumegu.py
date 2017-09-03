# -*- coding: utf-8 -*-

from __future__ import print_function

import lxml.etree as et
from parsel import Selector

from . import utils

class BaseParser(object):

    def __init__(self):
        self.current_idx = 0
        self.size = 0

    def __len__(self):
        return self.size

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.current_idx > self.size - 1:
            raise StopIteration()
        idx = self.current_idx
        self.current_idx += 1
        return self.parse(idx=idx)

    def parse(self):
        raise NotImplementedError

class DomParser(BaseParser):

    def __init__(self, data, url, url2,
                 query_entry,
                 query_title,
                 query_id=None,
                 query_link=None,
                 query_content=None):
        BaseParser.__init__(self)

        self.query_entry = query_entry
        self.query_title = query_title
        self.query_id = query_id
        self.query_link = query_link
        self.query_content = query_content

        self.items = Selector(data).css(self.query_entry)
        self.size = len(self.items)
        self.url = url
        self.url2 = url2

    def parse(self, idx=0):

        title = utils.strip_tags(self.items[idx].css(self.query_title).extract_first())

        if self.query_id:
            entry_id = self.items[idx].css(self.query_id).xpath('@id').extract_first()
        else:
            entry_id = None

        if self.query_link:
            url = utils.merge_url(self.url, self.items[idx].css(self.query_link).xpath('@href').extract_first())
        else:
            url = self.url2 or self.url

        if self.query_content:
            content = utils.strip_tags(''.join(self.items[idx].css(self.query_content).extract()).strip())
        else:
            content = None

        if entry_id:
            url = ''.join([url, '#', entry_id])
            entry_hash = utils.make_hash(''.join([url]))
        else:
            entry_hash = utils.make_hash(''.join([url, title]))

        return {
            'title': title,
            'content': content,
            'url': url,
            'media_urls': [utils.merge_url(self.url, _) for _ in self.items[idx].css('img').xpath('@src').extract()],
            'hash': entry_hash
        }

class XmlParser(BaseParser):

    def __init__(self, data,
                 prefix='xmlns',
                 namespaces='http://purl.org/rss/1.0/',
                 query_entry='item',
                 query_title='title/text()',
                 query_link='link/text()',
                 query_content='description/text()'):
        BaseParser.__init__(self)

        self.prefix = prefix
        self.namespaces = {prefix: namespaces}

        # RSS1.0またはRSS2.0の判定
        self.data = et.fromstring(data.encode('utf_8'))
        if self.data.tag == 'rss':
            self.query_entry = 'channel/%s' % (query_entry)
            self.query_title = query_title
            self.query_link = query_link
            self.query_content = query_content
        else:
            self.query_entry = '%s:%s' % (prefix, query_entry)
            self.query_title = '%s:%s' % (prefix, query_title)
            self.query_link = '%s:%s' % (prefix, query_link)
            self.query_content = '%s:%s' % (prefix, query_content)

        self.items = self.data.xpath(self.query_entry, namespaces=self.namespaces)
        self.size = len(self.items)

    def parse(self, idx=0):

        url = self.items[idx].xpath(self.query_link, namespaces=self.namespaces)[0]

        return {
            'title': utils.strip_tags(self.items[idx].xpath(self.query_title, namespaces=self.namespaces)[0]),
            'content': utils.strip_tags(self.items[idx].xpath(self.query_content, namespaces=self.namespaces)[0]),
            'url': url,
            'media_urls': [],
            'hash': utils.make_hash(url)
        }

class AtomParser(BaseParser):

    def __init__(self, data,
                 prefix='atom',
                 namespaces='http://www.w3.org/2005/Atom',
                 query_entry='entry',
                 query_id='id/text()',
                 query_title='title/text()',
                 query_link='link/@href'):
        BaseParser.__init__(self)

        self.prefix = prefix
        self.namespaces = {prefix: namespaces}
        self.query_entry = '%s:%s' % (prefix, query_entry)
        self.query_id = '%s:%s' % (prefix, query_id)
        self.query_title = '%s:%s' % (prefix, query_title)
        self.query_link = '%s:%s' % (prefix, query_link)

        self.data = et.fromstring(data.encode('utf_8'))
        self.items = self.data.xpath(self.query_entry, namespaces=self.namespaces)
        self.size = len(self.items)

    def parse(self, idx=0):
        return {
            'title': utils.strip_tags(self.items[idx].xpath(self.query_title, namespaces=self.namespaces)[0]),
            'content': None,
            'url': self.items[idx].xpath(self.query_link, namespaces=self.namespaces)[0],
            'media_urls': [],
            'hash': utils.make_hash(self.items[idx].xpath(self.query_id, namespaces=self.namespaces)[0])
        }
