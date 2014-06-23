#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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
        self.logger = logging.getLogger('global')
        self.db_handler.db = 'NTP'
        # self.db_handler.db.authenticate(os.environ['mongodb_user'],
        #                                 os.environ['mongodb_pass'])

        self.db_handler.table = 'meta'
        self.css_selector = {
            'dataset_url': 'table tr td a[href^="/NTPC/od/data/api/"]'
        }

    #### Yaml -> Web -> Meta ####

    @classmethod
    def load_config(cls, config_file=''):
        if not config_file:
            config = os.path.join(os.path.dirname(__file__), '..', '..',
                                  'config', 'ds_handlers', 'NTP.yaml')
        else:
            config = config_file
        return yaml.load(open(config))


    def update_all_meta(self):
        for dataset in self.config['datasets']:
            self.update_meta(dataset['oid'], self.get_meta(dataset['oid']))
        return 0


    def update_meta(self, oid, meta):
        if not self.db_handler.table == 'meta':
            self.db_handler.table = 'meta'
        return self.db_handler.update({'oid': oid}, meta)


    def list_meta(self):
        if not self.db_handler.table == 'meta':
            self.db_handler.table = 'meta'
        return self.db_handler.table.find({"dataset.id":{"$ne": None}})


    def get_meta(self, oid):
        soup = BeautifulSoup(urllib.urlopen(self.get_meta_url(oid)))
        print oid
        meta = {
            'id': oid,
            'name': util.clean_special_char(self.get_title(soup, oid)),
            'dataset': {
                'id': self.get_dataset_id(soup, oid),
                'formats': self.get_dataset_formats(soup)
            }
        }
        for f in self.config['meta_fields']:
            value = util.get_next_element(soup, f['alias'])
            # print value
            if f['name'] in self.config['split_text_fields']:
                value = util.split_text(value)
            elif f['name'] in ['ref_url', 'desc_file']:
                v = soup.find(text=f['alias'])
                if v:
                    value = v.next_element.find('a')['href']
            elif f['name'] == 'records':
                value = int(value)
            elif f['name'] == 'update_freq':
                value = util.get_next_element(soup, f['alias'], times=2).strip()
            elif f['name'] == 'description':
                value = util.replace_br(util.get_next_element(
                                            soup, f['alias'], string=False))
                if not value:
                    value = util.clean_special_char(
                                util.get_next_element(
                                    soup, f['alias'], times=2)).strip()
            meta.update({f['name']: value})

        for f in self.config['dataset'][oid].get('overwrite_fields', ''):
            meta.update({f['field']: f['value']})
        return meta

    def get_meta_url(self, oid):
        return (self.config['base_url'] +
                self.config['meta_url'] +
                urllib.urlencode({'oid': oid}))

    def get_title(self, soup, oid):
        if soup.find(id='title').string:
            return soup.find(id='title').string
        elif soup.find(id='title_0').string:
            return soup.find(id='title_0').string
        else:
            self.logger.warning("No title for {u}".format(
                                 u=self.get_meta_url(oid)))
            return ''
            # raise NoAttributeError("No title for {u}".format(
            #                        u=get_meta_url(oid)))

    def get_dataset_formats(self, soup):
        formats = []
        for l in soup.select(self.css_selector['dataset_url']):
            for format in self.config['data_formats']:
                if format in l['href']:
                    formats += [format]
        return formats

    def get_dataset_id(self, soup, oid):
        urls = soup.select(self.css_selector['dataset_url'])
        if len(urls) > 0:
            return re.findall('/NTPC/od/data/api/(\S+)/;', str(urls[0]))[0]
        else:
            self.logger.warning("No dataset_id for {u}".format(
                                 u=self.get_meta_url(oid)))
            return ''
            # raise NoAttributeError("No dataset_id for {t}".format(
            #                        t=self.get_meta_url(oid)))



    #### Meta -> json/xml/xls/etc -> Dataset ####

    def update_all_datasets(self, options=''):
        for d in self.list_meta():
            self.logger.info("getting dataset {d}, formats: {f}".format(
                              d=d['dataset']['id'], f=d['dataset']['formats']))
            self.get_dataset(dataset_id=d['dataset']['id'],
                             formats=d['dataset']['formats'])
            #print t
            #self.update_dataset(d['dataset']['id'],t)


    def update_dataset(self, dataset_id, data, force=False):
        if not self.db_handler.table == dataset_id:
            self.db_handler.table = dataset_id
        return self.db_handler.table.insert(data)


    def get_dataset(self, dataset_id, formats):
        # if not self.db_handler.table == 'meta':
        #     self.db_handler.table = 'meta'
        for format in formats:
            try:
                skip = 0
                dataset = self.parse_dataset(dataset_id, format,
                                             {'skip': skip})
                print dataset_id, len(dataset)
                while not len(dataset)%2000:
                    skip += 2000
                    dataset += self.parse_dataset(dataset_id, format,
                                                  {'skip': skip})
                    print dataset_id, len(dataset)
                    if len(dataset) >= 4000:
                        break

                return dataset
            except Exception, e:
                self.logger.exception("Except: parsing {d}, format {f}, {e}".format(
                                  d=dataset_id, f=format, e=e))
        self.logger.error("Failed to parse {d} from formats: {f}".format(
                           d=dataset_id, f=formats))
        # print "dataset"
        # print self.parse_dataset(dataset_id,
        #                           self.db_handler.table.find_one(
        #                               {"dataset.id": dataset_id}
        #                           )['dataset']['formats'][0])

    def get_dataset_url(self, dataset_id, format='json', options={}):
        # $format={format}&$top={top}&$skip={skip}&
        # $orderby={orderby}&$filter={field} eq {value}
        opt = {'id': dataset_id, 'format': format, 'top': 0, 'skip': 0,
               'orderby': '', 'field': '', 'value': ''}
        opt.update(options)
        url = (self.config['base_url'] +
               self.config['data_url'].format(**opt))
        self.logger.debug("Getting dataset {i} from url: {u}".format(
                           i=dataset_id, u=url))
        return url

    def parse_dataset(self, dataset_id, format, options):
        url = self.get_dataset_url(dataset_id, format, options)
        dataset = getattr(util, "parse_{f}_from_url".format(f=format))(url)

        if format == 'json':
            pass
        elif format == 'xml':
            pass
        elif format in ['xls', 'xlsx']:
            pass
        else:
            self.logger.error("dataset format {f} is not recognized".format(
                               f=format))
        return dataset

    #### datasets -> data ####

    # def get_all_datasets(self):
    #     for dataset in self.list_datasets():
    #         print dataset['dataset']['id']

    # def list_datasets()



    if __name__ == '__main__':
        # TODO: unittest
        unittest.main()


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
