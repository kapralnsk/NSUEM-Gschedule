# -*- coding: utf-8 -*-
import datetime
from apiclient.discovery import build


class Event(object):
    summary = location = start_date = end_date = recurrence_rule = None


class GoogleCalendar(object):

    def __init__(self, schedule):
        self.schedule = schedule
        self.start_date = self.set_semester_start()
        self.name = ''  # TODO naming logic
        self.time_zone = 'Asia/Novosibirsk'

    @staticmethod
    def set_semester_start():
        today = datetime.datetime.today()
        if today.month >= 8:
            start_date = today.replace(month=9, day=1)
        else:
            start_date = today.replace(month=2, day=1)

        if start_date.weekday() == 6:
            start_date = start_date.replace(month=2, day=2)
        return start_date

    # def form_events(self):
    #     return map(lambda item: Event())

    def set_start_dates(self):
        pass

    def build_calendar(self, oauth2decorator):

        service = build('calendar', 'v3')
        http = oauth2decorator.http()
        calendar = service.calendars().insert(body={
            'summary': self.name,
            'timeZone': self.time_zone
        }).execute(http=http)

        # insert events

