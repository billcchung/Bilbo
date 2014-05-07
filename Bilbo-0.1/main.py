#!/usr/bin/env python
__author__ = 'cchung'

import optparse
import lib.data_source_handlers
import lib.db_handler
import lib.utils


def main(dest):
    pass


if __name__ == "__main__":
    p = optparse.OptionParser()
    p.add_option('-c', '--conf-dir', dest='base_dir', default='.',
                 help='default conf dir, can be a splunk dir')
    p.add_option('-d', '--diag-dir', dest='diag_dir', default='',
                 help='diag conf, the untar-ed diag dir')

    (opts, args) = p.parse_args()
    print opts, args
    ret_code = main(**opts.__dict__)
    exit(ret_code)
