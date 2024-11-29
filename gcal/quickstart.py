import json
import logging
import sys
import datetime as dt
from render.render import RenderHelper
# from display.display import DisplayHelper  # Ensure you have the correct import for DisplayHelper
from pytz import timezone
from gcal.gcal import GcalHelper
from power.power import PowerHelper
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

def refresh_token(credentials_path):
    creds = Credentials.from_authorized_user_file(credentials_path)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(credentials_path, 'w') as token:
            token.write(creds.to_json())
    return creds

def main():
    # Create and configure logger
    logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
    logger = logging.getLogger('maginkcal')
    logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
    logger.setLevel(logging.INFO)
    logger.info("Starting daily calendar update")

    try:
        # Load configuration from config.json
        config_path = r'C:\Users\Sara\Desktop\MagInkCal\config.json'
        logger.info(f"Loading configuration from {config_path}")
        
        # Debugging: Check if the file exists
        if not os.path.exists(config_path):
            logger.error(f"Configuration file {config_path} does not exist.")
            sys.exit(1)
        
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        logger.info(f"Made it here configuration from {config_path}")

        # Extract values from the configuration
        displayTZ = timezone(config['displayTZ'])
        thresholdHours = config['thresholdHours']
        maxEventsPerDay = config['maxEventsPerDay']
        isDisplayToScreen = config['isDisplayToScreen']
        isShutdownOnComplete = config['isShutdownOnComplete']
        batteryDisplayMode = config['batteryDisplayMode']
        weekStartDay = config['weekStartDay']
        dayOfWeekText = config['dayOfWeekText']
        screenWidth = config['screenWidth']
        screenHeight = config['screenHeight']
        imageWidth = config['imageWidth']
        imageHeight = config['imageHeight']
        rotateAngle = config['rotateAngle']
        is24hour = config['is24h']
        calendars = config['calendars']
        logger.info(f"Made it hereerereerer Loading configuration from {config_path}")

        # Establish current date and time information
        logger.info("Initializing PowerHelper")
        powerService = PowerHelper()
        logger.info("PowerHelper initialized")

        logger.info("Syncing time with PowerHelper")
        powerService.sync_time()
        logger.info("Time synced with PowerHelper")

        logger.info("Getting battery level from PowerHelper")
        currBatteryLevel = powerService.get_battery()
        logger.info('Battery level at start: {:.3f}'.format(currBatteryLevel))

        currDatetime = dt.datetime.now(displayTZ)
        logger.info("Time synchronised to {}".format(currDatetime))
        currDate = currDatetime.date()
        calStartDate = currDate - dt.timedelta(days=((currDate.weekday() + (7 - weekStartDay)) % 7))
        calEndDate = calStartDate + dt.timedelta(days=(5 * 7 - 1))
        calStartDatetime = displayTZ.localize(dt.datetime.combine(calStartDate, dt.datetime.min.time()))
        calEndDatetime = displayTZ.localize(dt.datetime.combine(calEndDate, dt.datetime.max.time()))

        # Refresh Google Calendar API token
        credentials_path = r'C:\Users\Sara\Desktop\MagInkCal\token.json'
        creds = refresh_token(credentials_path)

        # Using Google Calendar to retrieve all events within start and end date (inclusive)
        start = dt.datetime.now()
        gcalService = GcalHelper(creds)
        eventList = gcalService.retrieve_events(calendars, calStartDatetime, calEndDatetime, displayTZ, thresholdHours)
        logger.info("Calendar events retrieved in " + str(dt.datetime.now() - start))

        # Populate dictionary with information to be rendered on e-ink display
        calDict = {'events': eventList, 'calStartDate': calStartDate, 'today': currDate, 'lastRefresh': currDatetime, 'batteryLevel': currBatteryLevel}

        # Instantiate RenderHelper with the configuration values
        render_helper = RenderHelper(imageWidth, imageHeight, rotateAngle)

        # Instantiate DisplayHelper with the configuration values
        # display_helper = DisplayHelper(screenWidth, screenHeight)

        # Use render_helper and display_helper to perform rendering and display tasks
        # For example:
        # render_helper.render_calendar(calDict)
        # display_helper.update(blackimg, redimg)

        # Check if configured to shutdown safely
        logger.info("Checking if configured to shutdown safely - Current hour: {}".format(currDatetime.hour))

    except Exception as e:
        logger.error("An error occurred: {}".format(e))
        sys.exit(1)

if __name__ == '__main__':
    main()