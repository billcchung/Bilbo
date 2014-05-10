#!/usr/bin/env python

"""
The handler for New TaiPei open data website

"""

__author__ = 'cchung'

import time
import json
import os
import ds_base
from .. import utils


class NTP(ds_base.BaseDataSourceHandler):

    def __init__(self, abc):
        super(NTP, self).__init__()
        pass

    def update_meta(self):
        pass


def main(url, dataId, format, name, replace='', **kwargs):
    print locals()
    top = 2000
    skip = 0
    sleep_sec = 5
    results = []
    while True:
        try:
            print url.format(**locals())
            request = utils.util.json_parser(url.format(**locals()), **kwargs)
            skip += top
            results += request
            if len(request) < top:
                break
        except Exception, e:
            print e
            time.sleep(sleep_sec)
    utils.util.write_result(results, dataId+name+'.json')
    print len(json.load(open(os.path.join(results_dir, dataId+name+'.json'))))
    return 0



