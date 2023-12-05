#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" console_weather
  opyright (C) 2023 Hao HUANG
  Resume of file :
    This file is used to display the weather information on the console.
"""
############################################################################

# import public packages

# import third-party packages

# import private packages
import API_caller

# import settings
import settings

def main():
    if settings.WEATHER:
        weather = API_caller.weather_API(settings.WEATHER_API_KEY, settings.WEATHER_CITY)
        weather.show_current_weather_information()
        # weather.show_forecast_information(days=5)


if __name__ == "__main__":
    main()

# End of console_weather.py