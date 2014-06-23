#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'cchung'

import os
import re
import yaml
import logging
import urllib2
import json
import unittest
import xmltodict
import types
import xml.etree.ElementTree as etree
from bs4 import BeautifulSoup


handler_format = ('[%(asctime)s] %(levelname)s '
                  '%(module)s:%(lineno)d:%(funcName)s - %(message)s')
# stream_hdlr_fmt = '[%(asctime)s] %(levelname)s %(message)s'
date_format = '%Y-%m-%d %H:%M:%S %Z'
log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'log')
if not os.path.exists(log_dir): os.mkdir(log_dir)

if "global_logger" not in globals():
    logging.basicConfig(level=logging.DEBUG,
                        format=handler_format,
                        datefmt=date_format,
                        filename=os.path.join(log_dir, "Bilbo.log"),
                        filemode='a+')
    global_logger = logging.getLogger('global')
    # console = logging.StreamHandler()
    # console.setLevel(logging.INFO)
    # console.setFormatter(logging.Formatter(fmt=stream_hdlr_fmt,
    #                                        datefmt=date_fmt))
    # global_logger.addHandler(console)

## excel loader: https://pypi.python.org/pypi/xlrd


# def next_element(soup, text):
#     found = soup.find(text=text)
#     if found:
#         return found.find_parent().find_next_sibling().string
#     else:
#         return ''

#### Beautiful Soup utils

def get_next_element(soup, text, times=1, string=True):
    element = soup.find(text=text)
    if element:
        for t in xrange(times):
            element = getattr(element, 'next_element')
        if string:
            return element.string
        else:
            return element
    else:
        return ''

def split_text(text, delimiters='', dict=False):
    if not delimiters:
        delimiters = u'\.|;|,|、|，'
    l = filter(None, [t.strip() for t in re.split(delimiters, text) if t])
    if dict:
        d = {}
        for i in l:
            if ':' in i: d.update(dict([i.split(':', 1)]))
        return { k: v for d in l for k, v in dict([i.split(':', 1)]).items() }
    else:
        return l

    # return filter(None, [t.strip() for t in re.split(delimiters, text)])

def replace_br(element, replace='\n'):
    text = ''
    for elem in element.recursiveChildGenerator():
        if isinstance(elem, types.StringTypes):
            text += elem.strip()
        elif elem.name == 'br':
            text += replace
    return text

def clean_special_char(text, rdict={}):
    # if not rdict:
    #     rdict = {
    #         u'\u3001': ', ',
    #         ur'[\u3000\.\s]+': '',
    #         '\r': ' ',
    #         '\t': ' ',
    #         '\n': ' '
    #     }
    # TODO: handle special char cleanup options
    if text:
        #robj = re.compile('|'.join(rdict.keys()))
        #return robj.sub(lambda m: rdict[m.group(0)], text).strip()
        return re.sub(u'[、　\.\s\t\n\r ]+', ' ', text).strip()
        # return re.sub(u'\u3001', ', ', re.sub(ur'[\u3000\.\s]+', '', text))
    else:
        return ''

# def clean_special_char(text, options={}):
#     # TODO: handle special char cleanup options
#     if text:
#         return re.sub(u'\u3001', ', ', re.sub(ur'[\u3000\.\s]+', '', text))
#     else:
#         return ''

#### Data parsing utils

def parse_json_from_url(url):
    passwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passwd_mgr.add_password(None, url, '', '')
    auth = urllib2.HTTPBasicAuthHandler(passwd_mgr)
    opener = urllib2.build_opener(auth)
    urllib2.install_opener(opener)
    request = urllib2.Request(url)
    return eval(urllib2.urlopen(request).read())

def parse_xml_from_url(url):
    tree = etree.parse(urllib2.urlopen(url))
    root = tree.getroot()
    return xml_to_dict(root)

def parse_xls_from_url(url, **kwargs):
    raise

def parse_xlsx_from_url(url, **kwargs):
    """
     just an alias of xls for now, hopefully it can handle both.
    """
    return parse_xls_from_url(**kwargs)

def parse_csv_from_url():
    raise


def xml_to_dict(el):
    """
        taken from:
      http://stackoverflow.com/questions/127606/
             editing-xml-as-a-dictionary-in-python#answer-2303733
    """
    d={}
    if el.text:
        d[el.tag] = el.text
    else:
        d[el.tag] = {}
    children = el.getchildren()
    if children:
        d[el.tag] = map(xml_to_dict, children)
    return d


#### Misc utils

def read_multiline_json(filename):
    """ read multline json (dict) file to list
    @param:
        file: @string

    @return:
        data: @list
    """
    data = []
    with open(filename) as f:
        for line in f:
            data.append(json.loads(line))
    return data


def write_result(results, filename, directory=''):
    """ write results to file

    @params:
        results: @string
        filename: @string
        directory: @string

    @return:
        0: @int, successful

    """
    log = open(os.path.join(directory, filename), 'a+')
    log.write((json.dumps(results)+'\n').encode('UTF-8'))
    log.close()
    return 0


def url_request_to_dict(url, user='', passwd=''):
    """ Open url and convert to dict, used for json data pages
    @params:
        url: @string
        user: @string, username for basic auth
        passwd: @string, password for basic auth
    @return:
        data: @dict
    """
    passwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passwd_mgr.add_password(None, url, user, passwd)
    auth = urllib2.HTTPBasicAuthHandler(passwd_mgr)
    opener = urllib2.build_opener(auth)
    urllib2.install_opener(opener)
    request = urllib2.Request(url)
    return eval(urllib2.urlopen(request).read())


######## Tests ########
class TestUtils(unittest.TestCase):

    def setUp(self):
        self.soup = BeautifulSoup(urllib2.urlopen('http://en.wikipedia.org'))

    def tearDown(self):
        pass

    def test_get_next_element_simple(self):
        self.assertEqual(get_next_element(self.soup, text='Wikipedia'), ",")

    def test_parse_json_from_url(self):
        url = 'http://data.ntpc.gov.tw/NTPC/od/data/api/PHB108/?$format=json'
        results = parse_json_from_url(url)
        self.assertEqual(results[0]['tel'], '2219-3391')

    def test_parse_xml_form_url(self):
        url = 'http://data.ntpc.gov.tw/NTPC/od/data/api/PHB108/?$format=xml'
        results = parse_xml_from_url(url)
        self.assertEqual(results['data'][0]['row'][2]['tel'], '2219-3391')

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUtils)
    unittest.TextTestRunner(verbosity=2).run(suite)
    # # TODO: unittest
    # unittest.main()