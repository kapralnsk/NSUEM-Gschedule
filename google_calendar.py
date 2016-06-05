# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime, timedelta
from apiclient.discovery import build

from settings import DEFAULT_TIMEZONE


class Event(object):
    summary = location = start_date = end_date = recurrence_rule = None


class GoogleCalendar(object):

    def __init__(self, schedule):
        self.schedule = schedule
        self.start_date = self.set_semester_start()
        self.set_start_dates()
        semester_num = 1 if self.start_date.month == 9 else 2
        self.name = '{year}_{semester_num}_semester'.format(year=self.start_date.year, semester_num=semester_num)
        self.time_zone = DEFAULT_TIMEZONE
        self.events = self.form_events()

    @staticmethod
    def set_semester_start():
        today = datetime.today()
        if today.month >= 8:
            start_date = today.replace(month=9, day=1)
        else:
            start_date = today.replace(month=2, day=1)

        if start_date.weekday() == 6:
            start_date = start_date.replace(month=2, day=2)
        return start_date

    def form_events(self):
        return map(self.serialize_exercise, self.schedule)

    def serialize_exercise(self, exercise):
        exercise_end = exercise.start_date + timedelta(hours=1, minutes=30)
        semester_end = exercise.start_date + timedelta(days=90)
        return {
            'summary': '{} ({})'.format(exercise.name, exercise.type),
            'location': exercise.room,
            'start': {
                'dateTime': '{date}T{time}:00'.format(date=exercise.start_date.strftime('%Y-%m-%d'),
                                                  time=exercise.start_date.strftime('%H:%M')),
                'timeZone': 'Asia/Novosibirsk'
            },
            'end': {
                'dateTime': '{date}T{time}:00'.format(date=exercise_end.strftime('%Y-%m-%d'),
                                                  time=exercise_end.strftime('%H:%M')),
                'timeZone': self.time_zone
            },
            'recurrence': [
                'RRULE:FREQ=WEEKLY;INTERVAL=2;UNTIL={}T210000Z'.format(semester_end.strftime("%Y%m%d"))
            ]
        }

    def set_start_dates(self):
        week_delta = timedelta(days=7)
        two_week_delta = timedelta(days=14)

        for exercise in self.schedule:
            # TODO NAMING
            delta_to_semester_start = timedelta(days=self.start_date.weekday() - exercise.weekday)
            is_first_week = exercise.week == 1
            if is_first_week:
                before_semester_start = self.start_date.weekday() < exercise.weekday
                is_semester_start = self.start_date.weekday() < exercise.weekday
                if before_semester_start:
                    exercise.start_date = (self.start_date - delta_to_semester_start) + two_week_delta
                elif is_semester_start:
                    exercise.start_date = self.start_date
                else:
                    exercise.start_date = self.start_date + delta_to_semester_start
            else:
                exercise.start_date = self.start_date + delta_to_semester_start + week_delta

    def build_calendar(self, oauth2decorator):
        service = build('calendar', 'v3')
        service.calendars().insert(body={
            'summary': self.name,
            'timeZone': self.time_zone
        }).execute(http=oauth2decorator.http())

        # insert events

