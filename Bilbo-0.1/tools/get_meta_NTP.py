#!/usr/bin/env python

__author__ = 'cchung'
import codecs
import os
import sys
import re
import yaml
import optparse
import urllib2

from bs4 import BeautifulSoup

class NoTitleException(Exception):
    pass


def next_element(soup, text):
    found = soup.find(text=text)
    if found:
        return found.find_parent().find_next_sibling().string
    else:
        return ''

def get_title(soup):
    if soup.find(id='title').string:
        return soup.find(id='title').string
    elif soup.find(id='title_0').string:
        return soup.find(id='title_0').string
    else:
        raise NoTitleException()

def clean_special_char(text, options={}):
    # TODO: handle special char cleanup options
    if text:
        return re.sub(u'\u3001', ', ', re.sub(ur'[\u3000\.\s]+', '', text))
    else:
        return ''

def main(config_file, out_file):
    meta = {}
    config = yaml.load(open(config_file))
    for data_set in config['dataSets']:
        id = data_set['url'].split('oid=')[1]
        full_url = config['baseUrl'] + data_set['url']
        print full_url
        request = urllib2.urlopen(full_url)
        soup = BeautifulSoup(request)
        meta[id] = {'name': clean_special_char(get_title(soup)),
                    'data_url': {}}

        for f in config['meta_fields']:
            meta[id].update({f['alias']:
                    clean_special_char(next_element(soup, f['name']))})

        for l in soup.select('table tr td a[href^="/NTPC/od/"]'):
            for data_type in config['data_types']:
                if data_type in l['href']:
                    meta[id]['data_url'].update({data_type: l['href']})
        #     meta[id].update({f: get_sibling(soup, f)})
    yaml.dump(meta, open(out_file, 'a+'))


if __name__ == "__main__":
    p = optparse.OptionParser()
    default_config = os.path.join(os.path.dirname(__file__), '..', 'config',
                                  'data_source_handlers', 'NTP.yaml')
    default_out_file = os.path.join(os.path.dirname(__file__), 'out.yaml')
    p.add_option('-c', '--config', dest='config_file', default=default_config,
                 help='config file')
    p.add_option('-o', '--out-file', dest='out_file', default=default_out_file,
                 help='output file')
    (opts, args) = p.parse_args()
    print opts, args
    ret_code = main(**opts.__dict__)
    exit(ret_code)