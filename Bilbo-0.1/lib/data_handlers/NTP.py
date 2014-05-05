#!/usr/bin/env python

"""
The handler for New TaiPei open data website

"""

__author__ = 'cchung'

import time
import json
import os

from ..util import util


def main(url, dataId, format, name, replace='', **kwargs):
    print locals()
    top = 2000
    skip = 0
    sleep_sec = 5
    results = []
    while True:
        try:
            print url.format(**locals())
            request = util.json_parser(url.format(**locals()), **kwargs)
            skip += top
            results += request
            if len(request) < top:
                break
        except Exception, e:
            print e
            time.sleep(sleep_sec)
    util.write_result(results, dataId+name+'.json')
    print len(json.load(open(os.path.join(results_dir,dataId+name+'.json'))))
    return 0


