# -*- coding: utf-8 -*-

import logging
import threading

import megumegu.database as database
import megumegu.utils as utils
from megumegu.megumegu import Megumegu
from megumegu.settings import settings

logging.basicConfig(filename=settings.get('LOG_FILE'), format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(settings.get('LOG_LEVEL'))

def main():
    try:
        db = database.Mysql(host=settings.get('MYSQL_HOST'),
                            user=settings.get('MYSQL_USER'),
                            passwd=settings.get('MYSQL_PASS'),
                            db=settings.get('MYSQL_DB'))
        sites = db.get_sites()

        # Site option example
        # sites = [{
        #     'id': 0,
        #     'name': 'Example Domain',
        #     'url': 'https://example.com/',
        #     'url2': None,
        #     'schedule': '* * * * *',
        #     'model': 'DOM',
        #     'query_entry': 'div',
        #     'query_id': None,
        #     'query_title': 'h1::text',
        #     'query_link': None,
        #     'query_content': 'p',
        #     'options': None,
        #     'start_tag': '',
        #     'end_tag': '',
        #     'latest_hash': None,
        #     'latest_title': None,
        #     'notification': True
        # }]

        if sites:
            sites = utils.filter_schedule(sites)

        if sites:
            for site in sites:
                t = threading.Thread(target=Megumegu, kwargs=site)
                t.start()

    except Exception as e:
        logger.exception(e)

if __name__ == '__main__':
    main()
