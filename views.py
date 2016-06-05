# -*- coding: utf-8 -*-
__author__ = 'alexandr'

import os
from oauth2client.appengine import OAuth2DecoratorFromClientSecrets
import nsuemScheduleParser
import cgi
from webapp2 import RequestHandler
from settings import JINJA_ENVIRONMENT


decorator = OAuth2DecoratorFromClientSecrets(
  os.path.join(os.path.dirname(__file__), 'client_secrets.json'),
  'https://www.googleapis.com/auth/calendar')



class CustomRequestHandler(RequestHandler):

    def sharap_cookie(self):
        # кука имени Шариповой! :)
        if self.request.cookies.get('sharap') is not None:
            params = {'sharap': 'true', }

        if self.request.get('sharap', default_value='no') != 'no':
            self.response.set_cookie('sharap', 'true')
            params = {'sharap': 'true', }

    def get(self):
        self.sharap_cookie()

    def post(self):
        self.sharap_cookie()


class GroupSelectionPage(CustomRequestHandler):

    def get(self):
        super(GroupSelectionPage, self).get()
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        params = {}  # temporary fix

        self.response.write(template.render(params))


class DoTheMagic(CustomRequestHandler):

    def get(self):
        self.redirect('/')

    @decorator.oauth_required
    def post(self):
        super(DoTheMagic, self).post()
        group = cgi.escape(self.request.get('group-selector'))
        schedule = nsuemScheduleParser.getEventsList(group)

        # Get the authorized Http object created by the decorator.
        http = decorator.http()

        # making a calendar for current semester
        semesterStart = nsuemScheduleParser.setSemesterStart()
        if semesterStart.month >= 8:
            anotherYear = int(semesterStart.strftime('%y')) + 1
            year = semesterStart.strftime('%y-') + str(anotherYear) + '_1'
        else:
            anotherYear = int(semesterStart.strftime('%y')) - 1
            year = str(anotherYear) + '-' + semesterStart.strftime('%y') + '_2'

        calendarName = 'semester_' + year
        calendar = {
            'summary': calendarName,
            'timeZone': 'Asia/Novosibirsk'
            }
        createdCalendar = service.calendars().insert(body=calendar).execute(http=http)

        for event in schedule:
            calendarEvent = event
            service.events().insert(calendarId=createdCalendar['id'], body=calendarEvent).execute(http=http)

        template = JINJA_ENVIRONMENT.get_template('templates/magic.html')
        params = {}  # temporary fix

        self.response.write(template.render(params))


class ItsAlive(CustomRequestHandler):
    def get(self):
        super(ItsAlive, self).get()
        template = JINJA_ENVIRONMENT.get_template('templates/itsalive.html')

        params = {}  # temporary fix

        self.response.write(template.render(params))
