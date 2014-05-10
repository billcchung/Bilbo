#!/usr/bin/env python
__author__ = 'cchung'

import os
import time
import yaml
import optparse
import lib.ds_handlers
import lib.db_handlers
import lib.utils
import thread

def get_data(ds_handler):
    """
        Get data based on the meta
    """
    while True:
        for dataset in ds_handler.list_datasets():
            if dataset['last_update']-time.time() > dataset['update_frequency']:
                ds_handler.get_data(dataset['id'])
                # the update_time will be the real time that we get the data
                ds_handler.update_meta(dataset['id'],'last_update', time.time())


def main(config_file):
    config = yaml.load(open(config_file))
    ds_handlers = {}
    for data_source in config['data_sources']:
        ds_handlers[data_source] = getattr(lib.ds_handlers, data_source)()
        ds_handlers[data_source].db_handler = lib.db_handlers.MongoDb()
        thread.start_new_thread(get_data, [ds_handlers[data_source]])
        raise



if __name__ == "__main__":
    default_config = os.path.join(os.path.dirname(__file__),
                                  'config', 'main.yaml')
    p = optparse.OptionParser()
    p.add_option('-c', '--config', dest='config_file', default=default_config,
                 help='main config file')

    (opts, args) = p.parse_args()
    print opts, args
    ret_code = main(**opts.__dict__)
    exit(ret_code)
