#!/usr/bin/env python
__author__ = 'cchung'


import os
import sys
import time
import yaml
import threading
import optparse

#sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
#print os.environ['PYTHONPATH']
from lib.ds_handlers import *
# import lib.ds_handlers.NTP
from lib.db_handlers import *
from lib.utils import *
print sys.modules[__name__]

def get_data(ds_handler):
    """
        Get data based on the meta
    """
    while True:
        print ds_handler.db_handler
        for dataset in ds_handler.list_datasets():
            if dataset['last_update']-time.time() > dataset['update_frequency']:
                ds_handler.get_data(dataset['id'])
                # the update_time will be the real time that we get the data
                ds_handler.update_meta(dataset['id'],
                                       {'last_update': time.time()})


def main(config_file):
    config = yaml.load(open(config_file))
    threads = []
    for data_source in config['data_sources']:
        db_handler = mongodb.MongoDb()
        ds_handler = getattr(globals()[data_source['name']],
                                       data_source['name'])(db_handler)

        # ds_handler = eval('lib.ds_handlers.NTP.NTP(db_handler)')
        threads += [threading.Thread(target=get_data, args=(ds_handler,))]

    for thread in threads: thread.start()
    for thread in threads: thread.join()

    return 0


if __name__ == "__main__":
    default_config = os.path.join(os.path.dirname(__file__),
                                  'config', 'main.yaml')
    ret_code = main(default_config)
    exit(ret_code)
#     p = optparse.OptionParser()
#     p.add_option('-c', '--config', dest='config_file', default=default_config,
#                  help='main config file')
#
#     (opts, args) = p.parse_args()
#     print opts, args
#     ret_code = main(**opts.__dict__)
#     exit(ret_code)
