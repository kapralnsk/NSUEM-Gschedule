# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import urllib2
from bs4 import BeautifulSoup
import datetime
from settings import BASE_URL


def changeWeek(week):
    if week == 1:
        return 2
    elif week == 2:
        return 1


def setSemesterStart():
    """setting semester start date
    return:getDate datetime
    """
    getDate = datetime.datetime.today()
    if getDate.month >= 8:
        startDate = getDate.replace(month=9, day=1)
        if startDate.weekday() == 6:
            startDate.replace(month=9, day=2)
    else:
        startDate = getDate.replace(month=2, day=1)
        if startDate.weekday() == 6:
            startDate = startDate.replace(month=2, day=2)
    return startDate


class Exercise(object):
    def __init__(self):
        self.week = 1
        self.weekday = 0
        self.time = self.type = self.name = self.room = None


def getEventsList(group):
    """makes an events list
    :param group - string. group ID
    :return eventsList - list.
    """
    # fetching table

    page = urllib2.urlopen(BASE_URL + 'group/' + group)
    soup = BeautifulSoup(page, 'html5lib')

    # limiting soup only to the table
    table = soup.find("table", {"class": "table table-hover table-bordered table-condensed"})
    tableSoup = BeautifulSoup(unicode(table), 'html5lib')
    currentRow = tableSoup.tbody.tr

    eventsList = []
    week = 2

    # welcome to the PAIN
    while currentRow is not None:
        if not currentRow.contents:
            currentRow = currentRow.find_next('tr')
        else:
            cell = currentRow.td

            # processing cell
            while cell is not None:

                # processing empty cells (might be a func)
                if cell.contents[0] == u' ':
                    if cell.next_sibling is not None:
                        if not cell.next_sibling['id']:  # TODO: and this
                            week = changeWeek(week)  # TODO: and this
                    else:
                        week = changeWeek(week)
                    cell = cell.next_sibling
                    continue

                exercise = Exercise()

                try:
                    cellCSS_ID = cell['id'].encode('utf-8')
                except KeyError:
                    exercise.week = changeWeek(week)

                    if cell.b is None:
                        exercise.type = 'Л'
                        cellData = getTD_Data(cell)
                    else:
                        exercise.type = 'С'
                        cellData = getTD_Data(cell.b)

                    if cellData is None:
                        currentRow = currentRow.find_next('tr')
                        week = changeWeek(week)
                        break

                    exercise.name = cellData['name']
                    exercise.room = cellData['room']
                    exercise.weekday = weekday
                    exercise.time = time
                    eventsList.append(formCalEvent(exercise))
                else:
                    if cellCSS_ID[0:3] == 'day':
                        weekday = int(cellCSS_ID[4])
                    elif cellCSS_ID[0:4] == 'time':
                        time = cell.div.get_text()
                cell = cell.next_sibling

            # check if end of table is reached
            currentRow = currentRow.find_next('tr')


    return eventsList


def getTD_Data(scope):
    if scope.div is None:
        return None

    TD_Data = {}

    data = scope.div.get_text().split(',')
    TD_Data['name'] = data[0]
    TD_Data['room'] = data[1][:6]
    return TD_Data


def formCalEvent(exercise):
    """
    Forming Google Calendar event using iCal notation
    data:tuple
    params::
    data - tuple: data, parsed from the page
    """
    # setting start date
    # if start date = Sunday, move 1 day forward
    semesterStart = setSemesterStart()

    if semesterStart.month == 9:
        rruleEnd = semesterStart.replace(month=12, day=31)
    else:
        rruleEnd = semesterStart.replace(month=3, day=31)
    rruleEnd.replace()
    rruleEnd = rruleEnd.strftime("%Y%m%d")

    exerciseStart = setExerciseStartDateTime(exercise, semesterStart)
    exerciseLength = datetime.timedelta(hours=1, minutes=30)
    exerciseEnd = exerciseStart + exerciseLength

    event = {
    'summary': '{} ({})'.format(exercise.name, exercise.type),
    'location': exercise.room,
    'start': {
    'dateTime': exerciseStart.strftime('%Y-%m-%d') + 'T' + exerciseStart.strftime('%H:%M') + ':00',
    'timeZone': 'Asia/Novosibirsk'
    },
    'end': {
    'dateTime': exerciseEnd.strftime('%Y-%m-%d') + 'T' + exerciseEnd.strftime('%H:%M') + ':00',
    'timeZone': 'Asia/Novosibirsk'
    },
    'recurrence': [
        'RRULE:FREQ=WEEKLY;INTERVAL=2;UNTIL=' + rruleEnd + "T210000" + 'Z'
    ]
    }
    return event


def setExerciseStartDateTime(exercise, semesterStart):
    weekdaysDelta = datetime.timedelta(days=semesterStart.weekday() - exercise.weekday)
    plus14DaysDelta = datetime.timedelta(days=14)

    if semesterStart.weekday() > exercise.weekday:
        startDate = semesterStart - weekdaysDelta + plus14DaysDelta
    elif semesterStart.weekday() == exercise.weekday:
        startDate = semesterStart
    elif semesterStart.weekday() < exercise.weekday:
        weekdaysDelta = datetime.timedelta(days=exercise.weekday - semesterStart.weekday())
        startDate = semesterStart + weekdaysDelta

    if exercise.week == 2:
        startDate += datetime.timedelta(days=7)

    startTime = datetime.datetime.strptime(exercise.time, '%H:%M')
    startDate = startDate.replace(hour=startTime.hour, minute=startTime.minute)

    return startDate
