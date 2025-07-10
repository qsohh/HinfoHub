#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" crypto_price_API
    opyright (C) 2025 Hao HUANG
    Resume of file :
        In this file, we define the class crypto_price_API.
        This is still a test file, and when finished, the class will be moved to the API_caller.py file.
"""

# import public packages
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import logging

# import third-party packages
import requests

# import private packages
from exception import API_caller_Exception
import API_caller


class latest_price_Binance():
    def __init__(self, symbols: list[str] = ["BTCUSDC", "BNBUSDC", "EURIUSDC"]):
        self.base_url = "https://api.binance.com/api/v3/ticker/price"
        self._response = None
        self._symbols = symbols
        logging.debug(f"latest_price_Binance object created: {self}")

    def get_response(self, url_modifier: str = "") -> requests.Response:
        """*get the response from the API*

        use url_modifier and updateparm to modify the url and parameters if needed.
        parameters:
            url_modifier: the url modifier
        output:
            the response from the API
        """
        self._timestamp = datetime.utcnow().isoformat()
        self._response = requests.get(self.base_url+url_modifier)
        # check the status code
        if self._response.status_code != 200:
            # !! TODO: clarify according to the error code and / or message
            # save the error message to the log file, to be improved
            logging.error(f"Error: {self._response.status_code}")
            logging.error(f"Error: {self._response.text}")
            # raise the exception
            raise API_caller_Exception(f"Error: {self._response.status_code}, {self._response.text}")
        logging.info(f"response status code: {self._response.status_code}")
        return self._response

    def show_latest_price(self) -> dict[str, float]:
        """*show the latest price of the crypto currencies*
        
        output:
            the latest price of the crypto currencies
        """
        response = self.get_response()
        data = response.json()
        prices = {item['symbol']: item['price'] for item in data if item['symbol'] in self._symbols}
        return prices
    
    def __str__(self) -> str:
        return f"latest_price_Binance(base_url={self.base_url}, symbols={self._symbols})"
    
    def print_latest_price(self):
        """*print the latest price of the crypto currencies*
        
        This method is used to print the latest price of the crypto currencies.
        """
        prices = self.show_latest_price()
        if not prices:
            raise API_caller_Exception("No prices found for the specified symbols.")
        logging.info("Latest Crypto Prices at time {}:".format(self._timestamp))
        print("Latest Crypto Prices at time {}:".format(self._timestamp))
        for symbol, price in prices.items():
            logging.info(f"{symbol}: {price} USDC")
            print(f"{symbol}: {price} USDC")

class Binance_kline():
    """*Binance_kline class*
    
    This class is used to get the kline data from the Binance API.
    It is now being implemented.
    """
    def __init__(self, symbol: str = "BTCUSDC", interval: str = "1h", limit: int = 500, start_time: str = None, end_time: str = None):
        """*Initialize the Binance_kline class*"""
        self.base_url = "https://api.binance.com/api/v3/klines"
        self._symbol = symbol
        self._interval = interval
        self._limit = limit
        self._start_time = start_time
        self._end_time = end_time
        self._response = None
        self._df = None
        self._df_signals = None
        self._signal_score = None
        logging.debug(f"Binance_kline object created: {self}")

    def get_response(self, url_modifier: str = "") -> requests.Response:
        """*get the response from the Binance API for kline data*

        use url_modifier and updateparm to modify the url and parameters if needed.
        parameters:
            url_modifier: the url modifier
        output:
            the response from the API
        """
        params = {
            'symbol': self._symbol,
            'interval': self._interval,
            'limit': self._limit,
            'startTime': self._start_time,
            'endTime': self._end_time
        }
        self._timestamp = datetime.utcnow().isoformat()
        self._response = requests.get(self.base_url + url_modifier, params=params)
        # check the status code
        if self._response.status_code != 200:
            logging.error(f"Error: {self._response.status_code}")
            logging.error(f"Error: {self._response.text}")
            raise API_caller_Exception(f"Error: {self._response.status_code}, {self._response.text}")
        logging.info(f"response status code: {self._response.status_code}")
        return self._response

    def get_kline_data(self) -> pd.DataFrame:
        """*get the kline data from the Binance API*

        output:
            the kline data from the Binance API
        """
        response = self.get_response()
        data = response.json()
        if not data:
            raise API_caller_Exception("No kline data found for the specified parameters.")
        # Convert the data to a pandas DataFrame
        columns = ['open_time', 'open_price', 'high_price', 'low_price', 'close_price', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
        df = pd.DataFrame(data, columns=columns)
        # drop the 'ignore' column as it is not needed
        df.drop(columns=['ignore'], inplace=True)
        # Convert timestamps to datetime
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        # Convert numeric columns to float
        numeric_columns = ['open_price', 'high_price', 'low_price', 'close_price', 'volume', 'quote_asset_volume', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']
        df[numeric_columns] = df[numeric_columns].astype(float)
        # Set the open_time as the index
        df.set_index('open_time', inplace=True)
        # Calculate additional columns : 'volume_weighted_average_price', 'buy_pressure', 'net_quote_flow', 'flow_momentum', 'ma_20', 'volatility', 'price_momentum'
        df['volume_weighted_average_price'] = np.where(df['volume'] != 0, df['quote_asset_volume'] / df['volume'], 0)
        df['buy_pressure'] = df['taker_buy_base_asset_volume'] / df['volume']
        df['net_quote_flow'] = 2 * df['taker_buy_quote_asset_volume'] - df['quote_asset_volume']
        df['flow_momentum'] = df['net_quote_flow'].diff().fillna(0)
        df['ma_20'] = df['volume_weighted_average_price'].rolling(window=20).mean()
        df['volatility'] = df['volume_weighted_average_price'].rolling(window=20).std()
        df['price_momentum'] = df['close_price'].diff().rolling(3).sum()
        self._df = df  # Store the DataFrame for later use
        logging.info(f"Kline data for {self._symbol} at time {self._timestamp}:")
        logging.debug(df.head())
        return df

    def plot_kline_data(self) -> bool:
        """*Plot the kline data from the Binance API*

        This method is used to plot the kline data from the Binance API via matplotlib.
        output:
            True if the kline data is shown successfully, False otherwise
        """
        try:
            df = self.get_kline_data()
            logging.info(f"Kline data for {self._symbol} at time {self._timestamp}:")
            print(f"Kline data for {self._symbol} at time {self._timestamp}:")
            logging.debug(df.head())
            # Plot the kline data
            fig1 = plt.figure(figsize=(12, 6))
            ax1 = fig1.add_subplot(231)
            ax2 = fig1.add_subplot(232)
            ax3 = fig1.add_subplot(233)
            ax4 = fig1.add_subplot(234)
            ax5 = fig1.add_subplot(235)
            ax6 = fig1.add_subplot(236)
            # plot the VWAP
            ax1.plot(df.index, df['volume_weighted_average_price'], label='VWAP', color='orange')
            # plot the 20-period moving average
            ax1.plot(df.index, df['ma_20'], label='20-period MA', color='brown')
            ax1.set_title('Volume Weighted Average Price (VWAP) and 20-period MA')
            # plot the kline
            ax2.plot(df.index, df['close_price'], label='Close Price', color='blue')
            ax2.fill_between(df.index, df['low_price'], df['high_price'], color='lightgray', alpha=0.5, label='High-Low Range')
            ax2.set_title('Kline Data')
            # plot the net quote flow
            ax3.plot(df.index, df['net_quote_flow'], label='Net Quote Flow', color='red')
            ax3.set_title('Net Quote Flow')
            # plot the flow momentum
            ax4.plot(df.index, df['flow_momentum'], label='Flow Momentum', color='purple')
            ax4.set_title('Flow Momentum')
            # plot the buy pressure
            ax5.plot(df.index, df['buy_pressure'], label='Buy Pressure', color='green')
            ax5.set_title('Buy Pressure')
            # plot the volatility
            ax6.plot(df.index, df['volatility'], label='Volatility', color='cyan')
            ax6.set_title('Volatility (20-period Std Dev)')
            fig1.suptitle(f"Kline Data for {self._symbol} at {self._timestamp}", fontsize=16)
            fig1.legend()
            plt.show()
            return True

        except API_caller_Exception as e:
            logging.error(f"Error showing kline data: {e}")
            return False

    def generate_signals(self) -> pd.DataFrame:
        """*Generate trading signals based on the kline data*

        This method generates trading signals based on the kline data.
        It is a placeholder for now and will be implemented later.
        output:
            a dictionary with the trading signals
        """
        # If the _df is not yet generated
        if self._df is None:
            self.get_response()
            self.get_kline_data()
        # Generate trading signals based on the kline data
        buy_pressure_upper_flag = self._df['buy_pressure'] > 0.7
        buy_pressure_lower_flag = self._df['buy_pressure'] < 0.3
        net_quote_flow_upper_flag = self._df['net_quote_flow'] > 0
        net_quote_flow_lower_flag = self._df['net_quote_flow'] < 0
        flow_momentum_upper_flag = self._df['flow_momentum'] > 0
        flow_momentum_lower_flag = self._df['flow_momentum'] < 0
        VWAP_upper_flag = self._df['volume_weighted_average_price'] > self._df['ma_20']
        VWAP_lower_flag = self._df['volume_weighted_average_price'] < self._df['ma_20']
        price_momentum_upper_flag = self._df['price_momentum'] > 0
        price_momentum_lower_flag = self._df['price_momentum'] < 0
        low_volatility_flag = self._df['volatility'] < 0.8 * self._df['volatility'].rolling(window=60).mean()
        rolling_window = 48  # 48 hours for 1-hour intervals, 2 days
        volatility_spike_flag = self._df['volatility'] > (self._df['volatility'].rolling(window=rolling_window).mean() + 2 * self._df['volatility'].rolling(window=rolling_window).std())
        # Create a DataFrame to hold the signals
        df_signals = pd.DataFrame(index=self._df.index)
        df_signals['buy_pressure_upper'] = buy_pressure_upper_flag
        df_signals['buy_pressure_lower'] = buy_pressure_lower_flag
        df_signals['net_quote_flow_upper'] = net_quote_flow_upper_flag
        df_signals['net_quote_flow_lower'] = net_quote_flow_lower_flag
        df_signals['flow_momentum_upper'] = flow_momentum_upper_flag
        df_signals['flow_momentum_lower'] = flow_momentum_lower_flag
        df_signals['VWAP_upper'] = VWAP_upper_flag
        df_signals['VWAP_lower'] = VWAP_lower_flag
        df_signals['price_momentum_upper'] = price_momentum_upper_flag
        df_signals['price_momentum_lower'] = price_momentum_lower_flag
        df_signals['low_volatility'] = low_volatility_flag
        df_signals['volatility_spike'] = volatility_spike_flag
        self._df_signals = df_signals
        # Log the signals
        logging.info(f"Trading signals for {self._symbol} at time {self._timestamp}:")
        logging.debug(df_signals.head())
        print(f"Trading signals for {self._symbol} at time {self._timestamp}:")
        return df_signals

    def evaluate_signal_score(self, strategy_name: str = "default") -> pd.DataFrame:
        """*Evaluate the signal score based on the trading signals*

        This method evaluates the signal score based on the trading signals.
        It is a placeholder for now and will be implemented later.
        output:
            a DataFrame with the signal scores
        """
        if self._df_signals is None:
            self.generate_signals()
        # self._signal_score has two columns: 'positive_score' and 'negative_score'
        self._signal_score = pd.DataFrame(index=self._df_signals.index)
        if strategy_name in ["default", "st1"]:
            self._signal_score['positive_score'] = (
                self._df_signals['buy_pressure_upper'].astype(int) +
                self._df_signals['net_quote_flow_upper'].astype(int) +
                self._df_signals['flow_momentum_upper'].astype(int) +
                self._df_signals['VWAP_upper'].astype(int) +
                self._df_signals['low_volatility'].astype(int)
            )
            self._signal_score['negative_score'] = (
                self._df_signals['buy_pressure_lower'].astype(int) +
                self._df_signals['net_quote_flow_lower'].astype(int) +
                self._df_signals['flow_momentum_lower'].astype(int) +
                self._df_signals['VWAP_lower'].astype(int) +
                self._df_signals['low_volatility'].astype(int)
            )
            # Normalize the scores to be between 0 and 1
            self._signal_score['positive_score'] = self._signal_score['positive_score'] / 5
            self._signal_score['negative_score'] = self._signal_score['negative_score'] / 5
        else:
            raise API_caller_Exception(f"Strategy {strategy_name} is not implemented.")

        # Evaluate a final score
        def classify_signal(row, threshold=0.5):
            if row['positive_score'] > threshold and row['negative_score'] < threshold:
                return 'positive'
            elif row['negative_score'] > threshold and row['positive_score'] < threshold:
                return 'negative'
            else:
                return 'neutral'
        self._signal_score['final_signal'] = self._signal_score.apply(classify_signal, axis=1)
        logging.info(f"Signal scores for {self._symbol} at time {self._timestamp}:")
        logging.debug(self._signal_score.head())
        return self._signal_score

    def plot_price_with_signal_score(self):
        """*Plot the price with the signal score*

        This method plots the price with the signal score.
        It is a placeholder for now and will be implemented later.
        """
        if self._df is None:
            self.get_kline_data()
        if self._signal_score is None:
            self.evaluate_signal_score()
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        fig.suptitle(f"Price and Signal Scores for {self._symbol}", fontsize=16)
        ax1.plot(self._df.index, self._df['volume_weighted_average_price'], color='orange', label='VWAP')
        ax1.plot(self._df.index, self._df['ma_20'], color='brown', label='MA 20')
        ax2 = ax1.twinx()
        mask_pos = self._signal_score['positive_score'] > 0.5
        ax2.plot(
            self._df.index[mask_pos], 
            self._signal_score['positive_score'][mask_pos], 
            'g.', 
            label='Positive Score > 0.5'
        )

        mask_neg = self._signal_score['negative_score'] > 0.5
        ax2.plot(
            self._df.index[mask_neg], 
            self._signal_score['negative_score'][mask_neg], 
            'r.', 
            label='Negative Score > 0.5'
        )
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()

        for idx, row in self._signal_score.iterrows():
            if row['final_signal'] == 'positive':
                ax1.axvline(idx, color='green', alpha=0.1)
            elif row['final_signal'] == 'negative':
                ax1.axvline(idx, color='red', alpha=0.1)

        plt.tight_layout()
        fig.legend()
        plt.show()


# End of file crypto_caller.py