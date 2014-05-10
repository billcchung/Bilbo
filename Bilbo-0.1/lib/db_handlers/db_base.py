#!/usr/bin/env python

__author__ = 'cchung'

import abc

class BaseDBHandler(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, host, port, auth):
        self.host = host
        self.port = port
        self.auth = auth

    @abc.abstractmethod
    def connect(self):
        """ Connect ot the database """


