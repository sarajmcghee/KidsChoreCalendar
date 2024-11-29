#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script generates a calendar as an HTML file and converts it to an image
using imgkit, avoiding the need for a WebDriver. The resulting image is processed
to extract grayscale and red portions, which are then sent to the eInk display.
"""

import imgkit
from datetime import timedelta
from PIL import Image
import pathlib
import logging


class RenderHelper:

    def __init__(self, width, height, angle):
        self.logger = logging.getLogger('maginkcal')
        self.currPath = str(pathlib.Path(__file__).parent.absolute())
        self.htmlFile = self.currPath + '/calendar.html'  # Absolute path without "file://"
        self.imageWidth = width
        self.imageHeight = height
        self.rotateAngle = angle

    def get_screenshot(self):
        """
        Render the HTML file to a PNG image using imgkit.
        """
        options = {
            'format': 'png',
            'width': self.imageWidth,
            'height': self.imageHeight,
            'quiet': '',
            'enable-local-file-access': ''  # Add this option
        }

        output_file = self.currPath + '/calendar.png'
        imgkit.from_file(self.htmlFile, output_file, options=options)
        self.logger.info('Screenshot captured and saved to file.')

        redimg = Image.open(output_file)  # Load the image
        rpixels = redimg.load()  # Create the pixel map
        blackimg = Image.open(output_file)  # Load the image again
        bpixels = blackimg.load()  # Create the pixel map

        for i in range(redimg.size[0]):  # Loop through every pixel in the image
            for j in range(redimg.size[1]):
                if rpixels[i, j][0] <= rpixels[i, j][1] and rpixels[i, j][0] <= rpixels[i, j][2]:  # If not red
                    rpixels[i, j] = (255, 255, 255)  # Change it to white in the red image bitmap
                elif bpixels[i, j][0] > bpixels[i, j][1] and bpixels[i, j][0] > bpixels[i, j][2]:  # If red
                    bpixels[i, j] = (255, 255, 255)  # Change to white in the black image bitmap

        redimg = redimg.rotate(self.rotateAngle, expand=True)
        blackimg = blackimg.rotate(self.rotateAngle, expand=True)

        self.logger.info('Image colours processed. Extracted grayscale and red images.')
        return blackimg, redimg

    def get_day_in_cal(self, startDate, eventDate):
        delta = eventDate - startDate
        return delta.days

    def get_short_time(self, datetimeObj, is24hour=False):
        datetime_str = ''
        if is24hour:
            datetime_str = '{}:{:02d}'.format(datetimeObj.hour, datetimeObj.minute)
        else:
            if datetimeObj.minute > 0:
                datetime_str = '.{:02d}'.format(datetimeObj.minute)

            if datetimeObj.hour == 0:
                datetime_str = '12{}am'.format(datetime_str)
            elif datetimeObj.hour == 12:
                datetime_str = '12{}pm'.format(datetime_str)
            elif datetimeObj.hour > 12:
                datetime_str = '{}{}pm'.format(str(datetimeObj.hour % 12), datetime_str)
            else:
                datetime_str = '{}{}am'.format(str(datetimeObj.hour), datetime_str)
        return datetime_str

    def process_inputs(self, calDict):
        """
        Generate the calendar HTML based on the input dictionary, then render it to images.
        """
        calList = [[] for _ in range(35)]  # List for 5 weeks of calendar days

        # Retrieve calendar configuration
        maxEventsPerDay = calDict['maxEventsPerDay']
        batteryDisplayMode = calDict['batteryDisplayMode']
        dayOfWeekText = calDict['dayOfWeekText']
        weekStartDay = calDict['weekStartDay']
        is24hour = calDict['is24hour']

        # Populate calendar list with events
        for event in calDict['events']:
            idx = self.get_day_in_cal(calDict['calStartDate'], event['startDatetime'].date())
            if idx >= 0:
                calList[idx].append(event)
            if event['isMultiday']:
                idx = self.get_day_in_cal(calDict['calStartDate'], event['endDatetime'].date())
                if idx < len(calList):
                    calList[idx].append(event)

        # Read HTML template
        with open(self.currPath + '/calendar_template.html', 'r') as file:
            calendar_template = file.read()

        # Insert month header and battery icon
        month_name = str(calDict['today'].month)
        battLevel = calDict['batteryLevel']
        battText = 'batteryHide'

        if batteryDisplayMode == 1:
            battText = f'battery{min(int(battLevel // 20) * 20, 80)}'
        elif batteryDisplayMode == 2 and battLevel < 20.0:
            battText = 'battery0'

        # Populate day of week and events
        cal_days_of_week = ''.join(
            f'<li class="font-weight-bold text-uppercase">{dayOfWeekText[(i + weekStartDay) % 7]}</li>\n'
            for i in range(7)
        )

        cal_events_text = ''
        for i, day_events in enumerate(calList):
            currDate = calDict['calStartDate'] + timedelta(days=i)
            dayOfMonth = currDate.day
            cal_events_text += f'<li><div class="date{" text-muted" if currDate.month != calDict["today"].month else ""}">{dayOfMonth}</div>\n'
            for j, event in enumerate(day_events[:maxEventsPerDay]):
                cal_events_text += f'<div class="event{" text-muted" if currDate.month != calDict["today"].month else ""}">{event["summary"]}</div>\n'
            if len(day_events) > maxEventsPerDay:
                cal_events_text += f'<div class="event text-muted">{len(day_events) - maxEventsPerDay} more</div>\n'
            cal_events_text += '</li>\n'

        # Write calendar HTML
        with open(self.currPath + '/calendar.html', 'w') as htmlFile:
            htmlFile.write(calendar_template.format(
                month=month_name, battText=battText, dayOfWeek=cal_days_of_week, events=cal_events_text))

        # Render HTML to images
        calBlackImage, calRedImage = self.get_screenshot()
        return calBlackImage, calRedImage
