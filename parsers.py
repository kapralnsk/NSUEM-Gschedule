# -*- coding: utf-8 -*-
__author__ = 'alexandr'
import urllib2
from bs4 import BeautifulSoup
from settings import BASE_URL


class BaseParser(object):

    def __init__(self, url):
        self.page = urllib2.urlopen(BASE_URL + url)
        self.soup = BeautifulSoup(self.page)

    def parse(self):
        pass


class ScheduleParser(BaseParser):
    def parse(self):
        pass  # и тут общая логика, типа поскольку они парсят таблицу


class GroupsParser(BaseParser):
    def parse(self):
        pass


class GroupScheduleParser(ScheduleParser):
    pass


class TeacherScheduleParser(ScheduleParser):
    pass
