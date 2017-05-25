# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
import requests

from . import APP_VERSION
from .parsers import DomParser, XmlParser, AtomParser
from .error import MeguError
from .settings import settings, plugins
from .utils import enc_unicode, trim_html, unescape
from .database import Mysql

logger = logging.getLogger('megumegu.megumegu')

class Megumegu(object):

    def __init__(self, **kwargs):
        self.id = kwargs.pop('id')
        self.name = kwargs.pop('name')
        self.url = kwargs.pop('url')
        self.url2 = kwargs.pop('url2')
        self.last_title = kwargs.pop('last_title')
        self.model = kwargs.pop('model')
        self.query_entry = kwargs.pop('query_entry')
        self.query_title = kwargs.pop('query_title')
        self.query_id = kwargs.pop('query_id', None)
        self.query_link = kwargs.pop('query_link', None)
        self.query_content = kwargs.pop('query_content', None)
        self.options = kwargs.pop('options', None)
        self.start_tag = kwargs.pop('start_tag', None)
        self.end_tag = kwargs.pop('end_tag', None)
        self.notification = kwargs.pop('notification', False)

        self.updates = []
        self.content = None
        self.raw_content = None

        self.run()

    def get_content(self, retry=5):
        try:
            session = requests.Session()
            retries = requests.packages.urllib3.util.retry.Retry(total=retry, backoff_factor=0.1, status_forcelist=[403, 404, 500, 502, 503, 504])
            session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))
            session.mount('http://', requests.adapters.HTTPAdapter(max_retries=retries))

            resp = session.get(url=self.url, stream=True, headers={'User-Agent': settings.get('USER_AGENT', 'Megumegu/v%s' % APP_VERSION)}, timeout=settings.getint('TIMEOUT', 10))

            # レスポンスコードチェック
            if resp.status_code and not 200 <= resp.status_code < 300:
                raise MeguError('ResponseError(%s): %s (%s)' % (resp.status_code, self.name, resp.url))

            # サイトデータ処理
            self.raw_content = enc_unicode(resp.content)

            # サイトデータ整形
            self.content = self.raw_content
            if self.options:
                for opts in self.options.split(','):
                    if opts == 'trim':
                        self.content = trim_html(self.content, self.start_tag, self.end_tag)
                    elif opts == 'escape':
                        self.content = unescape(self.content)

        except requests.exceptions.RequestException as e:
            raise e
        except Exception as e:
            raise e

    def parse_content(self):
        if self.content:
            try:
                if self.model == 'DOM':
                    self.updates.append(DomParser(data=self.content,
                                                  url=self.url, url2=self.url2,
                                                  query_entry=self.query_entry,
                                                  query_title=self.query_title,
                                                  query_id=self.query_id,
                                                  query_link=self.query_link,
                                                  query_content=self.query_content).parse())
                elif self.model == 'XML':
                    self.updates.append(XmlParser(data=self.content).parse())
                elif self.model == 'ATOM':
                    self.updates.append(AtomParser(data=self.content).parse())
            except Exception as e:
                logger.error('ParserError: %s (%s)' % (self.name, self.url))
                logger.exception(e)

    def notify_content(self):
        if self.updates and \
           self.last_title != self.updates[0]['title']:

            db = Mysql(host=settings.get('MYSQL_HOST'),
                       user=settings.get('MYSQL_USER'),
                       passwd=settings.get('MYSQL_PASS'),
                       db=settings.get('MYSQL_DB'))

            # 過去のアップデートからハッシュ値を照合
            skip = False
            for h in db.get_update_hash(self.id):
                if 'hash' in h and h['hash'] == self.updates[0]['hash']:
                    skip = True
                    return
            if skip:
                return

            # データベースに登録
            db.insert_update(
                self.id,
                self.updates[0]['url'],
                self.updates[0]['title'],
                self.updates[0]['content'],
                self.updates[0]['hash'],
            )

            # 各サービスへ通知
            if self.notification:
                for module in plugins:
                    try:
                        module.Plugin.push(
                            name=self.name,
                            url=self.updates[0]['url'],
                            title=self.updates[0]['title'],
                            content=self.updates[0]['content'],
                            media_urls=self.updates[0]['media_urls'])
                    except Exception as e:
                        logger.error('PluginError: %s (%s)' % (self.name, self.url))
                        logger.exception(e)

            print(self.updates[0])

    def run(self):
        try:
            self.get_content()
            self.parse_content()
            self.notify_content()
        except Exception as e:
            logger.error(e)
