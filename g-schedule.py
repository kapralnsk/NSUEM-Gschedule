# -*- coding: utf-8 -*-
__author__ = 'Alexandr'

from google.appengine.api import users
import os
import cgi
import webapp2
import nsuemScheduleParser

from apiclient.discovery import build
from google.appengine.ext import webapp
from oauth2client.appengine import OAuth2DecoratorFromClientSecrets

# constants

HEADER_HTML = """\
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
  </head>
  <body>
"""

FOOTER_HTML = """\
  </body>
</html>
"""

WHITESPACE = '<br /><br />'

GROUP_SELECTION_FORM = """\
<form action="/dothemagic" method="post">
<select name="group-selector" style="width:100px; margin-bottom:10px">
<option name="1761" value="1761">1761</option>
<option name="1762" value="1762">1762</option>
<option name="2761" value="2761">2761</option>
</select>
<div><input type="submit" value="Ду зе мэджик"></div>
</form>
"""
# end of constants

decorator = OAuth2DecoratorFromClientSecrets(
  os.path.join(os.path.dirname(__file__), 'client_secrets.json'),
  'https://www.googleapis.com/auth/calendar')

service = build('calendar', 'v3')

class GroupSelectionPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(HEADER_HTML)
        self.response.write(GROUP_SELECTION_FORM)
        self.response.write(FOOTER_HTML)

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

        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(HEADER_HTML)
        self.response.write('magic should be done')
        self.response.write(FOOTER_HTML)


application = webapp2.WSGIApplication([
    ('/', GroupSelectionPage),
    ('/dothemagic', DoTheMagic),
    (decorator.callback_path, decorator.callback_handler()),
], debug=True)
