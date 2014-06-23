#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
The handler for New TaiPei tour website
http://tour.ntpc.gov.tw/

"""

__author__ = 'cchung'

from ds_base import *

class TOUR_NTP(BaseDataSourceHandler):

    def __init__(self, db_handler='', config_file=''):
        super(TOUR_NTP, self).__init__(db_handler, config_file)
        self.logger = logging.getLogger('global')
        self.db_handler.db = 'TOUR_NTP'
        # self.db_handler.db.authenticate(os.environ['mongodb_user'],
        #                                 os.environ['mongodb_pass'])

        self.db_handler.table = 'TOUR_NTP_FOOD'
        css_prefix = 'tr#ctl07_ctl10_pageControl_TR_SPG_'
        css_suffix = ' td.specpage_data_info_content'
        self.css_selector = {
            'name'      : 'div.specpage_data_title strong',
            'desc'      : 'div.specpage_data_desc',
            'addr'      : css_prefix + 'ADDR'     + css_suffix,
            'map'       : css_prefix + 'MAP'      + css_suffix,
            'tel'       : css_prefix + 'TEL'      + css_suffix,
            'open_hours': css_prefix + 'OPENTIME' + css_suffix,
        }

    @classmethod
    def load_config(cls, config_file=''):
        if not config_file:
            config = os.path.join(os.path.dirname(__file__), '..', '..',
                                  'config', 'ds_handlers', 'TOUR_NTP.yaml')
        else:
            config = config_file
        return yaml.load(open(config))

    def get_page_url(self, page):
        page_url = (self.config['base_url'] +
                    self.config['page_url'].format(p=page))
        self.logger.info("Getting page url: {u}".format(u=page_url))
        return page_url

    def get_store_url(self, url):
        store_url = self.config['base_url'] + url
        self.logger.info("Getting store url: {u}".format(u=store_url))
        return store_url
        # return self.config['base_url'] + self.config['store_url'].format(id=id)

    def select(self, soup, text, num=0):
        s = soup.select(text)
        if s:
            try:
                if s[num].contents[0].string:
                    return s[num].contents[0].string.strip()
                else:
                    self.logger.warn(u"element has no string, returning element")
                    return s[num]
            except Exception, e:
                self.logger.exception(u"Except: page {p}, text {t}".format(
                                       p=soup.title.string.strip(), t=text))
                return s[num]
        else:
            self.logger.warn(u"No item found for text: {t}, page {p}".format(
                              p=soup.title.string.strip(), t=text))
            return ''

    def update_data(self, data, force=False):
        return self.db_handler.table.insert(data)


    def get_dataset(self):
        for page in xrange(1, self.config['total_pages']):
            soup_page = BeautifulSoup(urllib.urlopen(self.get_page_url(page)))

            for s in soup_page.select('div.specpage_table_title'):
                store_url = self.get_store_url(s.a['href'])
                bs = BeautifulSoup(urllib.urlopen(store_url))
                r ={k:self.select(bs, v) for (k,v) in self.css_selector.items()}
                r.update({
                    'id': store_url.split('&id=')[1],
                    'url': store_url,
                })
                print r['url']
                self.update_data(r)