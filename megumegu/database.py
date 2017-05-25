# -*- coding: utf-8 -*-

from __future__ import print_function

import warnings
import MySQLdb

class QueryMixin(object):

    def sql(self):
        raise NotImplementedError

    def get_sites(self):
        return self.sql("""SELECT mm_site.id as id, name, mm_site.url as url, url2, schedule, notification, model, query_entry, query_id, query_title, query_link, query_content, start_tag, end_tag, options, mm_updates.title as last_title
                           FROM mm_site
                           LEFT JOIN mm_option ON mm_site.id = mm_option.site_id
                           LEFT JOIN mm_notification ON mm_site.id = mm_notification.site_id
                           LEFT JOIN (
                                SELECT max(id) as id, site_id
                                FROM mm_updates
                                GROUP BY site_id
                           ) last_update ON last_update.site_id = mm_site.id
                           LEFT JOIN mm_updates ON mm_site.id = last_update.site_id AND mm_updates.id = last_update.id
                           WHERE mm_site.enable is True
                           """)

    def get_update_hash(self, site_id, limit=2):
        return self.sql("""SELECT hash
                           FROM mm_updates
                           WHERE site_id = %s
                           ORDER BY id DESC
                           LIMIT %s
                           """, (site_id, limit))

    def insert_update(self, site_id, url, title, content, update_hash):
        param = {}
        param['site_id'] = site_id
        param['url'] = url
        param['title'] = title
        param['content'] = content
        param['hash'] = update_hash

        self.sql("""INSERT INTO mm_updates(%s) VALUES(%s)""", param)

        return self.get_last_insert_id()

class Mysql(QueryMixin):

    def __init__(self, host, user, passwd, db, port=3306, charset='utf8mb4'):
        warnings.filterwarnings('ignore', category=MySQLdb.Warning)
        try:
            self._connect = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, port=port, charset=charset)
            self.set_dict_cursor()
        except MySQLdb.Error as e:
            raise Exception(e)

    def __del__(self):
        if self._cursor:
            self._cursor.close()
        if self._connect:
            self._connect.close()

    def set_cursor(self):
        self._cursor = self._connect.cursor(MySQLdb.cursors.Cursor)

    def set_dict_cursor(self):
        self._cursor = self._connect.cursor(MySQLdb.cursors.DictCursor)

    def get_last_insert_id(self):
        return self._cursor.lastrowid

    def sql(self, query, values=()):
        try:
            if values != ():
                if isinstance(values, dict):
                    query = self.build_query(query, values)
                    values = tuple(values.values())
                elif isinstance(values, list):
                    values = tuple(values)
                elif not isinstance(values, tuple):
                    values = (values,)

                self._cursor.execute(query, values)

            else:
                self._cursor.execute(query)

        except Exception:
            raise

        self._connect.commit()

        return self._cursor.fetchall()

    def build_query(self, query, values):
        col = ', '.join(list(map(lambda x: x, values)))
        val = ', '.join(list(map(lambda x: '%s', values)))
        return query % (col, val)
