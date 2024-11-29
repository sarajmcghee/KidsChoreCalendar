#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This part of the code exposes functions to interface with the eink display
"""

import display.epd7in5_V2 as eink  # Ensure you have the correct import for your display
from PIL import Image
import logging

class DisplayHelper:
    def __init__(self, width, height):
        # Initialise the display
        self.logger = logging.getLogger('maginkcal')
        self.screenwidth = width
        self.screenheight = height
        self.epd = eink.EPD()  # Ensure this matches the class name in your driver file
        self.logger.info("Initializing e-paper display.")
        if self.epd.init() != 0:
            self.logger.error("Failed to initialize e-paper display!")
            raise RuntimeError("Failed to initialize e-paper display!")
        self.logger.info("E-paper display initialized successfully.")

    def update(self, blackimg, redimg):
        # Updates the display with the grayscale and red images
        self.logger.info("Updating the display with new images.")
        self.epd.display(blackimg)
        self.logger.info('E-Ink display update complete.')

    def calibrate(self, cycles=1):
        # Calibrates the display to prevent ghosting
        self.logger.info("Calibrating the display to prevent ghosting.")
        white = Image.new('1', (self.screenwidth, self.screenheight), 'white')
        black = Image.new('1', (self.screenwidth, self.screenheight), 'black')
        for _ in range(cycles):
            self.epd.display(black)
            self.epd.display(white)
            self.epd.display(white)
        self.logger.info('E-Ink display calibration complete.')

    def sleep(self):
        # Send E-Ink display to deep sleep
        self.logger.info("Putting the e-paper display to sleep.")
        self.epd.sleep()
        self.logger.info('E-Ink display entered deep sleep.')