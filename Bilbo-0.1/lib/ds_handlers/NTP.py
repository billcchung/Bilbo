#!/usr/bin/env python
"""
The handler for New TaiPei open data website

"""
__author__ = 'cchung'

from ds_base import *

class NoAttributeError(Exception):
    def __init__(self, msg=''):
        self.msg = msg


class NTP(BaseDataSourceHandler):

    def __init__(self, db_handler='', config_file=''):
        super(NTP, self).__init__(db_handler, config_file)
        self.db_handler.db = self.__class__.__name__
        self.css_selector = {
            'dataset_url':'table tr td a[href^="/NTPC/od/data/api/"]'
        }

    @classmethod
    def load_config(cls, config_file=''):
        if not config_file:
            config = os.path.join(os.path.dirname(__file__), '..', '..',
                                  'config', 'ds_handlers', 'NTP.yaml')
        else:
            config = config_file
        return yaml.load(open(config))

    #### Meta level ####

    def update_all_meta(self):
        for dataset in self.config['datasets']:
            self.update_meta(dataset['oid'], self.get_meta(dataset))
        return 0

    def update_meta(self, oid, meta):
        return self.db_handler.update({'oid': oid}, meta)

    def get_meta_url(self, oid):
        return (self.config['base_url'] +
                self.config['meta_url'] +
                urllib.urlencode({'oid': oid}))

    def get_meta(self, dataset):
        soup = BeautifulSoup(urllib.urlopen(self.get_meta_url(dataset['oid'])))
        meta = {
            'name': utils.util.clean_special_char(
                        self.get_title(soup, dataset['oid'])),
            'dataset': {
                'id': self.get_dataset_id(soup),
                'formats': self.get_dataset_formats(soup)
            }
        }
        for f in self.config['meta_fields']:
            meta.update({
                f['alias']: utils.util.get_next_element(soup, f['name'])
            })
        return meta

    def get_title(self, soup, oid):
        if soup.find(id='title').string:
            return soup.find(id='title').string
        elif soup.find(id='title_0').string:
            return soup.find(id='title_0').string
        else:
            raise NoAttributeError("No title for {u}".format(
                                   u=self.get_meta_url(oid)))

    #### Dataset level ####

    def get_dataset_url(self, dataset_id, format='json'):
        return (self.config['base_url'] +
                self.config['data_url'] +
                str(dataset_id) +
                urllib.urlencode({'format': format}))

    def get_dataset_id(self, soup):
        url = str(soup.select(self.css_selector['dataset_url'])[0])
        if id:
            return re.findall('/NTPC/od/data/api/(\S+)/;', url)
        else:
            raise NoAttributeError("No dataset_id for {t}".format(
                                   t=self.get_title(soup)))

    def get_dataset(self, dataset_id, **kwargs):
        return self.db_handler.find()

    def update_dataset(self):
        raise

    def get_dataset_formats(self, soup):
        formats = []
        for l in soup.select(self.css_selector['dataset_url']):
            for format in self.config['data_formats']:
                if format in l['href']:
                    formats += [format]
        return formats

# def main(url, dataId, format, name, replace='', **kwargs):
#     print locals()
#     top = 2000
#     skip = 0
#     sleep_sec = 5
#     results = []
#     while True:
#         try:
#             print url.format(**locals())
#             request = utils.util.json_parser(url.format(**locals()), **kwargs)
#             skip += top
#             results += request
#             if len(request) < top:
#                 break
#         except Exception, e:
#             print e
#             time.sleep(sleep_sec)
#     utils.util.write_result(results, dataId+name+'.json')
#     # print len(json.load(open(os.path.join(, dataId+name+'.json'))))
#     return 0
#
