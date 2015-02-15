# -*- coding: utf-8 -*-
__author__ = 'Alexandr'

import os
import cgi
import jinja2
import webapp2
import nsuemScheduleParser

from apiclient.discovery import build
from google.appengine.ext import webapp
from oauth2client.appengine import OAuth2DecoratorFromClientSecrets

# constants

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# end of constants

decorator = OAuth2DecoratorFromClientSecrets(
  os.path.join(os.path.dirname(__file__), 'client_secrets.json'),
  'https://www.googleapis.com/auth/calendar')

service = build('calendar', 'v3')

class GroupSelectionPage(webapp2.RequestHandler):

    def get(self):

        template = JINJA_ENVIRONMENT.get_template('index.html')
        params = {} # temporary fix

        # кука имени Шариповой! :)
        if self.request.cookies.get('sharap') is not None:
            params = {'sharap': 'true', }

        if self.request.get('sharap', default_value='no') != 'no':
            self.response.set_cookie('sharap', 'true')
            params = {'sharap': 'true', }

        self.response.write(template.render(params))



class DoTheMagic(webapp2.RequestHandler):

    def get(self):
        self.redirect('/')

    @decorator.oauth_required
    def post(self):

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
            createdEvent = service.events().insert(calendarId=createdCalendar['id'], body=calendarEvent).execute(http=http)

        template = JINJA_ENVIRONMENT.get_template('magic.html')
        params = {}  # temporary fix


        # кука имени Шариповой! :)
        if self.request.cookies.get('sharap') is not None:
            params = {'sharap': 'true', }

        self.response.write(template.render(params))


class ItsAlive(webapp2.RequestHandler):
    def get(self):

        template = JINJA_ENVIRONMENT.get_template('itsalive.html')

        params = {}  # temporary fix
        # кука имени Шариповой! :)
        if self.request.cookies.get('sharap') is not None:
            params = {'sharap': 'true', }

        self.response.write(template.render(params))


application = webapp2.WSGIApplication([
    ('/', GroupSelectionPage),
    ('/dothemagic', DoTheMagic),
    ('/its-alive', ItsAlive),
    (decorator.callback_path, decorator.callback_handler()),
], debug=True)
