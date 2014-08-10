#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'cchung'

import os
import sys
import time
import yaml
import threading
import optparse

from lib import *
print globals()
# from lib.ds_handlers import *
# from lib.db_handlers import *
# from lib.utils import *
print sys.modules[__name__]

def process_runner(ds_handler):
    """
        Process runner
    """
    while True:
        print ds_handler.db_handler

        ## update meta
        # TODO: if contorller.should_update_meta(ds_handler.)
        #ds_handler.update_all_meta()
        # ds_handler.update_all_datasets()
        # print len(ds_handler.get_dataset(dataset_id='ws_announce_activity', formats=['json']))
        ds_handler.get_dataset()
        raise

        ## udpate datasets

        #ds_handler.update_all_datasets()
        #for dataset in ds_handler.list_datasets():
        #    print dataset
        #    if dataset['last_update']-time.time() > dataset['update_frequency']:
        #        print dataset
                # ds_handler.update_dataset(dataset['id'])
                # # the update_time will be the real time that we get the data
                # ds_handler.update_meta(dataset['id'], {'last_update': time.time()})

def main(config_file):
    config = yaml.load(open(config_file))
    # TODO: make a controller
    threads = []
    for ds in config['data_sources']:
        db_handler = db_handlers.mongodb.MongoDb()
        db_handler.db = 'Loc'

        # ds_handler = getattr(globals()[ds['name']], ds['name'])(db_handler)
        ds_handler = getattr(getattr(ds_handlers, ds['name']),
                             ds['name'])(db_handler)
        # ds_handler = eval('lib.ds_handlers.NTP.NTP(db_handler)')
        threads += [threading.Thread(target=process_runner, args=(ds_handler,))]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
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
