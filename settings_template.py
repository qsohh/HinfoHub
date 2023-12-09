#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" settings
    opyright (C) 2023 Hao HUANG
    Resume of file :
        In this file, we define the basic settings for the program, such as the API key.
        Note that this file is not included in the repository. But a template is provided
        in order to help you to create your own settings.py.
"""
############################################################################

# import public packages
import logging

# import third-party packages

# import private packages

# logging settings
logger = logging.getLogger("Hinfo")
logging.basicConfig(filename="./Hinfo.log", level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")

# API settings

# weather API
# this application uses the weather API from https://www.weatherapi.com/
# you can get your API key from https://www.weatherapi.com/my/
# more details to be seen in README.md
WEATHER = True
WEATHER_API_KEY = "YOUR_API_KEY" # API key from https://www.weatherapi.com/
WEATHER_CITY = "Paris"

# End of settings.py