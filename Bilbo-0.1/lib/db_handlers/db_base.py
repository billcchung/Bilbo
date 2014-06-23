#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'cchung'

import abc
import os

class BaseDbHandler(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, host, port, user='', password=''):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    # @abc.abstractmethod
    # def connect(self):
    #     """ Connect ot the database """


