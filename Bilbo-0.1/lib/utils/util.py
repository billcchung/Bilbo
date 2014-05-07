#!/usr/bin/env python
__author__ = 'cchung'

import urllib2
import json
import os

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
