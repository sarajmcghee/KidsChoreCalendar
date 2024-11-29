import json
import logging
import sys
import datetime as dt
from render.render import RenderHelper
#from display.display import DisplayHelper  # Ensure you have the correct import for DisplayHelper
from pytz import timezone
from gcal.gcal import GcalHelper
from power.power import PowerHelper
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from PIL import Image
from display.epd7in5_V2 import EPD  # Replace with your display's driver

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
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
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

          # Initialize e-paper display
        epd = EPD()
        epd.init()
        epd.Clear()
        logger.info("E-paper display initialized successfully.")

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


        # Using Google Calendar to retrieve all events within start and end date (inclusive)
        start = dt.datetime.now()
        gcalService = GcalHelper()
        eventList = gcalService.retrieve_events(calendars, calStartDatetime, calEndDatetime, displayTZ, thresholdHours)
        logger.info("Calendar events retrieved in " + str(dt.datetime.now() - start))

        # Populate dictionary with information to be rendered on e-ink display
        calDict = {'events': eventList, 'calStartDate': calStartDate, 'today': currDate, 'lastRefresh': currDatetime,
                   'batteryLevel': currBatteryLevel, 'batteryDisplayMode': batteryDisplayMode,
                   'dayOfWeekText': dayOfWeekText, 'weekStartDay': weekStartDay, 'maxEventsPerDay': maxEventsPerDay,
                   'is24hour': is24hour}

        # Instantiate RenderHelper with the configuration values
        render_helper = RenderHelper(imageWidth, imageHeight, rotateAngle)
        calBlackImage, calRedImage = render_helper.process_inputs(calDict)
        calBlackImage.save("blackimg.png")
        calRedImage.save("redimg.png")
        logger.info("Rendered calendar images saved for verification.")

        if calBlackImage.size != (epd.width, epd.height):
            logger.info("Resizing image to match e-paper resolution...")
            calBlackImage = calBlackImage.resize((epd.width, epd.height))
        calBlackImage = calBlackImage.convert('1')  # Convert to 1-bit black-and-white mode

        if isDisplayToScreen:
            buffer = epd.getbuffer(calBlackImage)
            epd.display(buffer)
            #if currDate.weekday() == weekStartDay:
                # calibrate display once a week to prevent ghosting
                #displayService.calibrate(cycles=0)  # to calibrate in production
        logger.info("Calendar image displayed successfully.")

        # Put the display to sleep
        epd.sleep()
        logger.info("E-paper display put to sleep.")

        currBatteryLevel = powerService.get_battery()
        logger.info('Battery level at end: {:.3f}'.format(currBatteryLevel))
        # Check if configured to shutdown safely
        logger.info("Checking if configured to shutdown safely - Current hour: {}".format(currDatetime.hour))

    except Exception as e:
        logger.error("An error occurred: {}".format(e))
        sys.exit(1)

if __name__ == '__main__':
    main()