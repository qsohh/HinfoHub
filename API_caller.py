#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" API_caller
  opyright (C) 2023 Hao HUANG
  Resume of file :
    In this file, we define the class API_caller.
    This class is used to call the API of the website.
    The caller is realized via third-party package requests.
"""
############################################################################

# import public packages
import logging

# import third-party packages
import requests

# import private packages
from exception import API_caller_Exception


TF_YN = {True: "yes", False: "no"} # True or False to "yes" or "no"


class API_caller:
    def __init__(self, url: str, key: str, headers: dict | None = None):
        """*initialize the API caller*
        """
        self._url = url
        self._headers = headers
        self._params = {"key": key}
        self._response = None
        self.__key = key

    def __str__(self) -> str:
        return f"API_caller(url={self._url}, key={self.__key})"

    def show_url(self) -> str:
        return self._url

    def show_key(self) -> str:
        return self.__key

    def get_response(self, url_modifier: str = "", updateparm: dict = {}) -> requests.Response:
        """*get the response from the API*

        use url_modifier and updateparm to modify the url and parameters if needed
        parameters:
            url_modifier: the url modifier
            updateparm: the update parameters
        output:
            the response from the API
        """
        self._response = requests.get(self._url+url_modifier, headers=self._headers, params=self._params|updateparm)
        # check the status code
        if self._response.status_code != 200:
            # !! TODO: clarify according to the error code and / or message
            # save the error message to the log file, to be improved
            logging.error(f"Error: {self._response.status_code}")
            logging.error(f"Error: {self._response.text}")
            # raise the exception
            raise API_caller_Exception(f"Error: {self._response.status_code}")
        return self._response

    def get_json(self, url_modifier: str = "", updateparm: dict = {}) -> dict:
        """*get the json dict from the API*
        """
        self.get_response(url_modifier, updateparm)
        return self._response.json()


class weather_API(API_caller):
    def __init__(self, api_key: str):
        base_url = "http://api.weatherapi.com/v1/"
        self._response = None
        super().__init__(base_url, api_key)
        # log the creation of the object
        logging.debug(f"weather_API object created: {self}")

    def get_current_weather(self, location: str = "Paris", aqi: bool = True) -> dict:
        """*get the current weather*

        parameters:
            location: the location, name of the city (or zip code, to be tested)
            aqi: whether to include the aqi (air quality index)
        output:
            the json dict of the current weather
        """
        url_modifier = "current.json"
        updateparm = {"q": location, "aqi": TF_YN[aqi]}
        self._response = self.get_response(url_modifier, updateparm)
        return self._response.json()

    def get_forecast(self, location: str = "Paris", days: int = 3, aqi: bool = True, alerts: bool = True) -> dict:
        """*get the forecast*

        parameters:
            location: the location, name of the city (or zip code, to be tested)
            days: the number of days to forecast
            aqi: whether to include the aqi (air quality index)
            alerts: whether to include the alerts
        output:
            the json dict of the forecast
        """
        url_modifier = "forecast.json"
        updateparm = {"q": location, "days": days, "aqi": TF_YN[aqi], "alerts": TF_YN[alerts]}
        self._response = self.get_response(url_modifier, updateparm)
        return self._response.json()

    def show_current_weather_information(self) -> None:
        """*show the current weather information*
        """
        # check if the response has already been obtained
        if self._response is None:
            self.get_current_weather()
        # get the current weather information
        current = self._response.json()["current"]
        # show the current weather information
        print(f"Current weather in {self._response.json()['location']['name']}:")
        print(f"  Temperature: {current['temp_c']}°C (feels like {current['feelslike_c']}°C)")
        print(f"  Humidity: {current['humidity']}%")
        print(f"  Precipitation: {current['precip_mm']} mm")
        print(f"  Weather: {current['condition']['text']}")
        # show the air quality information
        print(f"Air quality:")
        print(f"  PM2.5: {current['air_quality']['pm2_5']} μg/m3")
        print(f"  PM10: {current['air_quality']['pm10']} μg/m3")

        return None


# End of file