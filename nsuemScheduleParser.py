# -*- coding: utf-8 -*-
__author__ = 'KAPRAL'

import urllib2
from bs4 import BeautifulSoup
import re
import datetime


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
        getDate = getDate.replace(month=9, day=1)
        if getDate.weekday() == 6:
            getDate.replace(month=9, day=2)
    else:
        getDate.replace(month=2, day=1)
        if getDate.weekday() == 6:
            getDate = getDate.replace(month=2, day=2)
    return getDate


def getEventsList(group):
    """makes an events list
    :param group - string. group ID
    :return eventsList - list.
    """
    # fetching table


    page = urllib2.urlopen("http://rasp.nsuem.ru/group/" + group)
    soup = BeautifulSoup(page).find("table", {"class": "table table-hover table-bordered table-condensed"})
    currentRow = soup.tbody.tr

    # TODO remove if now useless
    exercise = {
    'week': 1,
    'weekday': 0,
    'time': '',
    'type': '',
    'name': '',
    'room': ''
    }

    eventsList = []
    week = 2

    # welcome to the PAIN
    while currentRow is not None:
        try:
            wut = currentRow.contents[0]
        except IndexError:
            currentRow = currentRow.find_next('tr')
        else:
            cell = currentRow.td

            # processing cell
            while cell is not None:

                # processing colspaned cell
                # TODO: fix crash on colspaned cell (text:"Выходной")
                if cell.get('colspan') == 3:
                    cell = cell.next_sibling
                    continue

                # processing empty cells (might be a func)
                if cell.contents[0].encode('utf-8') == ' ':
                    if cell.next_sibling is not None:
                        try:
                            wut = cell.next_sibling['id']
                        except KeyError:
                            week = changeWeek(week)
                    else:
                        week = changeWeek(week)
                    cell = cell.next_sibling
                    continue

                try:
                    cellCSS_ID = cell['id'].encode('utf-8')
                except KeyError:
                    week = changeWeek(week)
                    exercise['week'] = week
                    if cell.b is None:
                        exercise['type'] = 'Л'
                        cellData = getTD_Data(cell)
                    else:
                        exercise['type'] = 'С'
                        cellData = getTD_Data(cell.b)
                    exercise['name'] = cellData['name']
                    exercise['room'] = cellData['room']
                    eventsList.append(formCalEvent(exercise))
                else:
                    if cellCSS_ID[0:3] == 'day':
                        exercise['weekday'] = int(cellCSS_ID[4])
                    elif cellCSS_ID[0:4] == 'time':
                        exercise['time'] = cell.div.get_text().encode('utf-8')
                cell = cell.next_sibling
            currentRow = currentRow.find_next('tr')

    return eventsList


def getTD_Data(scope):
    data = scope.div
    TD_Data = {}
    name = data.get_text().encode('utf-8')
    TD_Data['name'] = name[0:len(name) - 8]
    TD_Data['room'] = data.a.get_text().encode('utf-8')
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
        rruleEnd = semesterStart.replace(month=5, day=31)
    rruleEnd.replace()
    rruleEnd = rruleEnd.strftime("%Y%m%d")

    exerciseStart = setExerciseStartDateTime(exercise, semesterStart)
    exerciseLength = datetime.timedelta(hours=1, minutes=30)
    exerciseEnd = exerciseStart + exerciseLength

    event = {
    'summary': exercise['name'] + ' (' + exercise['type'] + ')',
    'location': exercise['room'],
    'start': {
    'datetime': exerciseStart.strftime('%Y%m%d') + 'T' + exerciseStart.strftime('%H%M') + '000',
    # TODO: возможно формат неверный
    'timezone': 'Russia/Novosibirsk'
    },
    'end': {
    'datetime': exerciseEnd.strftime('%Y%m%d') + 'T' + exerciseEnd.strftime('%H%M') + '000',
    'timezone': 'Russia/Novosibirsk'
    },
    'reccurrence': [
        'RRULE:FREQ=WEEKLY;INTERVAL=2;UNTIL=' + rruleEnd + "T210000"
    ]
    }
    return event


def setExerciseStartDateTime(exercise, semesterStart):
    weekdaysDelta = datetime.timedelta(days=semesterStart.weekday() - exercise['weekday'])
    plus14DaysDelta = datetime.timedelta(days=14)

    if semesterStart.weekday() > exercise['weekday']:
        startDate = semesterStart - weekdaysDelta + plus14DaysDelta
    elif semesterStart.weekday() == exercise['weekday']:
        startDate = semesterStart
    elif semesterStart.weekday() < exercise['weekday']:
        weekdaysDelta = datetime.timedelta(days=exercise['weekday'] - semesterStart.weekday())
        startDate = semesterStart + weekdaysDelta

    if exercise['week'] == 2:
        startDate += datetime.timedelta(days=7)

    startTime = datetime.datetime.strptime(exercise['time'], '%H:%M')
    startDate = startDate.replace(hour=startTime.hour, minute=startTime.minute)

    return startDate
