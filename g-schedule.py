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


        # TODO exceptions to check cookies? there's got to be another way
        # кука имени Шариповой! :)
        try:
            self.request.cookies['sharap']
        except KeyError:
            template = JINJA_ENVIRONMENT.get_template('index.html')
        else:
            template = JINJA_ENVIRONMENT.get_template('lena.html')
        if self.request.get('sharap', default_value='no') != 'no':
            self.response.set_cookie('sharap', 'true')
            template = JINJA_ENVIRONMENT.get_template('lena.html')

        self.response.write(template.render())


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

        self.response.write(template.render())


application = webapp2.WSGIApplication([
    ('/', GroupSelectionPage),
    ('/dothemagic', DoTheMagic),
    (decorator.callback_path, decorator.callback_handler()),
], debug=True)
