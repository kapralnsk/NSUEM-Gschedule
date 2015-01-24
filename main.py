__author__ = 'KAPRAL'

#from apiclient.discovery import build
#from oauth2client.file import Storage
#from oauth2client.client import OAuth2WebServerFlow
#from oauth2client.tools import run
#import httplib2
import nsuemScheduleParser

#FLOW = OAuth2WebServerFlow(
   # client_id='977232472779-bg8socn6o9mnev7vjhaghpai54nhi54n.apps.googleusercontent.com',
    #client_secret='ce2YEjOwz5AYPnys0Zd6njxM',
   # scope='https://www.googleapis.com/auth/calendar',
   # user_agent='NSUEM schedule grabber/0.1')


# If the Credentials don't exist or are invalid, run through the native client
# flow. The Storage object will ensure that if successful the good
# Credentials will get written back to a file.
#storage = Storage('calendar.dat')
#credentials = storage.get()
#if credentials is None or credentials.invalid == True:
  #credentials = run(FLOW, storage)

# Create an httplib2.Http object to handle our HTTP requests and authorize it
# with our good Credentials.
#http = httplib2.Http()
#http = credentials.authorize(http)

schedule = nsuemScheduleParser.getEventsList()
scheduleAsString = ' - '.join(schedule)
file = open('schedule.txt', 'w')
file.write(scheduleAsString)
file.close()
