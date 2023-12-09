#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" stock_analysis
    opyright (C) 2023 Hao HUANG
    Resume of file :
        In this file, we define the class of stock_analyser which is used to analyse the stock data.
        We read the data from the csv files sotred in the folder data.
        The price data could be obtained from Boursoama, and several other websites.
        The dividend data could be easily obtained from https://www.bnains.org/index.php.
        For this very first version, we only consider the price and the dividend, and to calculate the 
        RoI_annual (annual return on investment) and annual standard deviation.

        !!todo: IRR (internal rate of return)
"""
############################################################################

# import public packages
import os
import logging
import numpy as np

# import third-party packages
import pandas as pd

# import private packages


class stock_analyser:
    def __init__(self, stock_name: str):
        """*initialize the stock analyser*
        """
        self._stock_name = stock_name
        # read the stock data from the csv file
        # first check the current path
        current_path = os.getcwd()
        # then get the path of the stock data, if /data is not in the current path, then go to the parent path
        while "data" not in os.listdir(current_path):
            current_path = os.path.dirname(current_path)
        # check if the stock data is available
        if stock_name + "_price.csv" not in os.listdir(os.path.join(current_path, "data")):
            logging.error("The stock data of {} is not available.".format(stock_name))
            logging.error("Please download the stock data from Boursorama and proceed the data extraction. via [A FUNCTION TO BE DEFINED]")
            raise FileNotFoundError("The stock data of {} is not available.".format(stock_name))
        # get the path of the stock data
        self._stock_price = pd.read_csv(os.path.join(current_path, "data", stock_name + "_price.csv"), index_col=0)
        # get the path of the stock dividend
        stock_dividend_path = os.path.join(current_path, "data", stock_name + "_dividende.csv")
        if os.path.exists(stock_dividend_path):
            self._stock_dividend = pd.read_csv(stock_dividend_path, index_col=0)
        else:
            self._stock_dividend = {"None": None}
            logging.warning("The dividend data of {} is not available.".format(stock_name))


    def RoI(self, start_date: str = "03/01/2022", end_date: str = "LAST"):
        """*calculate the RoI (return on investment)*
        """
        if end_date == "LAST":
            end_date = self._stock_price.index[-1]
        # total number of days
        nb_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
        # total dividende after date_begin
        d = 0
        for date in self._stock_dividend.index:
            if pd.to_datetime(date) > pd.to_datetime(start_date):
                d += self._stock_dividend.loc[date, "dividende"]
        RoI_annual = ((self._stock_price.loc[end_date, "closing"] + d) / self._stock_price.loc[start_date, "closing"]) ** (365 / nb_days) - 1
        self._RoI_annual = RoI_annual
        return RoI_annual


    def SD(self, start_date: str = "03/01/2022", end_date: str = "LAST"):
        """*calculate the standard deviation*

        TODO: this SD should be normalized or not?
        """
        if end_date == "LAST":
            end_date = self._stock_price.index[-1]
        # total number of days
        nb_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
        # adjust the price by the dividendes
        self._stock_price["closing_adj"] = self._stock_price["closing"]
        for date in self._stock_dividend.index:
            if pd.to_datetime(date) > pd.to_datetime(start_date):
                self._stock_price.loc[:date, "closing_adj"] -= self._stock_dividend.loc[date, "dividende"]
        # calculate the mean price
        mean_price = self._stock_price.loc[start_date:end_date, "closing_adj"].mean()
        # calculate the standard deviation
        SD = np.sqrt(((self._stock_price.loc[start_date:end_date, "closing_adj"] - mean_price) ** 2).sum() / nb_days)
        SD_annual = SD * np.sqrt(365 / nb_days)
        self._SD_annual = SD_annual
        self._SD = SD
        return SD_annual, SD


    def calculate(self, start_date: str = "03/01/2022", end_date: str = "LAST"):
        """*calculate the annual RoI and annual standard deviation*
        """
        return self.RoI(start_date, end_date), *self.SD(start_date, end_date)


def treat_price(stock_name: str):
    """*treat the price data*

    This function is used to treat the price data from Boursorama.
    The price data can be downloaded from https://www.boursorama.com/cours/[certain_stock]/ via the button "Télécharger les cotations".
    Remeber to select the period of time (up to 10 years can be obtained).
    """
    current_path = os.getcwd()
    # then get the path of the stock data, if /data is not in the current path, then go to the parent path
    while "data" not in os.listdir(current_path):
        current_path = os.path.dirname(current_path)
    # get the path of the stock data with file name "[stock_name]_YYYY-MM-DD.txt"
    for file_name in os.listdir(os.path.join(current_path, "data")):
        if stock_name in file_name and ".txt" in file_name:
            break
    # read the price data as a list of lines
    with open(os.path.join(current_path, "data", file_name), "r") as f:
        lines = f.readlines()

    # extract the price and save them into dataframes
    data = {}
    for line in lines[1:]:
        line = line.strip()
        line = line.split("\t")
        date = line[0][:-6]
        data[date] = [float(line[1]), float(line[2]), float(line[3]), float(line[4]), int(line[5])]
    df = pd.DataFrame.from_dict(data, orient="index", columns=["open", "high", "low", "closing", "volume"])
    df.index.name = "date"
    # save the dataframe into csv file
    df.to_csv(os.path.join(current_path, "data", stock_name + "_price.csv"))
    return 1


def save_dividend(stock_name: str):
    """*save the dividend data*

    Now you have to add the dividend data manually, or to find a way to extract the dividend data from the website.
    Considering potential legal liabilities, I will not propose any way to extract the dividend data automatically.
    """
    dividend = {"DD/MM/YYYY": 0.00}
    df = pd.DataFrame.from_dict(dividend, orient="index", columns=["dividende"])
    df.index.name = "date"
    # save the dataframe into csv file
    current_path = os.getcwd()
    # then get the path of the stock data, if /data is not in the current path, then go to the parent path
    while "data" not in os.listdir(current_path):
        current_path = os.path.dirname(current_path)
    df.to_csv(os.path.join(current_path, "data", stock_name + "_dividende.csv"))
    return 1

# end of file