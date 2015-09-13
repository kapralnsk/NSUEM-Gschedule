# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import urllib2
from bs4 import BeautifulSoup
from settings import BASE_URL
from parser_results import Exercise


class BaseParser(object):
    """
    base class for all parsers
    """
    def __init__(self, url):
        self.page = urllib2.urlopen(BASE_URL + url)
        self.soup = BeautifulSoup(self.page)


class ScheduleParser(BaseParser):
    """
    schedule table parser
    """
    def parse(self):
        """
        parses schedule table
        """
        exercises = []
        table = self.soup.find("table", {"class": "table table-hover table-bordered table-condensed"})
        table_soup = BeautifulSoup(unicode(table), 'html5lib')
        rows = filter(lambda item: bool(item.contents), table_soup.tbody.contents)
        for row in rows:
            cells = row.contents
            for index, cell in enumerate(cells):
                if cell.attrs.get('class'):
                    if 'day-header' in cell.attrs.get('class'):
                        weekday = cell.attrs.get('id')[-1]
                        continue
                if cell.attrs.get('id'):
                    if 'time' in cell.attrs.get('id'):
                        time = cell.contents[0].text
                        continue
                if cell.b:
                    exercise_type = 'C'
                else:
                    exercise_type = 'Л'
                if cell.select('.mainScheduleInfo'):
                    exercise_info = cell.select('.mainScheduleInfo')[0].text.split(', ')
                    exercise = Exercise(week=index-1, weekday=weekday, time=time,
                                        type=exercise_type, name=exercise_info[0], room=exercise_info[1])
                    exercises.append(exercise)
        return exercises


class GroupsParser(BaseParser):
    """
    groups list parser
    """
    def parse(self):
        pass


class GroupScheduleParser(ScheduleParser):
    """
    parser for specific group schedule
    """
    def __init__(self, group):
        super(GroupScheduleParser, self).__init__(u'group/' + group)


class TeacherScheduleParser(ScheduleParser):
    """
    parser for specific teacher schedule
    """
    pass
