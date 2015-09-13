# -*- coding: utf-8 -*-
from parsers import GroupScheduleParser

__author__ = 'Alexandr'


class Schedule(object):

    def __init__(self, schedule_type, name):
        self.schedule_type, self.name = schedule_type, name
        if self.schedule_type == 'group':
            self.exercises = GroupScheduleParser(name).parse()
        else:
            raise KeyError('Invalid schedule type. Choices are: group, teacher')

    def exercises_by_weekday(self, weekday, week):
        return filter(lambda item: item.weekday == weekday and item.week == week, self.exercises)
