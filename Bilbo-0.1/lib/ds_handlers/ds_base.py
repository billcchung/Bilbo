#!/usr/bin/env python
__author__ = 'cchung'

import abc

class BaseDataSourceHandler(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def config(self):
        pass

    def __init__(self, abc):
        pass

    @abc.abstractmethod
    def update_meta(self):
        pass
