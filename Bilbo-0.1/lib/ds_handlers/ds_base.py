#!/usr/bin/env python
__author__ = 'cchung'

import abc
import time
import json
import os
import yaml
import urllib
import re
from bs4 import BeautifulSoup
from .. import utils

class BaseDataSourceHandler:
    __metaclass__ = abc.ABCMeta

    def __init__(self, db_handler='', config_file=''):
        self.db_handler = db_handler
        self.config = self.load_config(config_file)

    @abc.abstractmethod
    def load_config(self, conf_file):
        pass

    # @property
    # def db_handler(self):
    #     return self.db_handler
    #
    # @db_handler.setter
    # def db_handler(self, db_handler):
    #     self.db_handler = db_handler

    # @abc.abstractmethod
    # def update_meta(self):
    #     pass

    # @abc.abstractmethod
    # def get_data(self):
    #     pass
