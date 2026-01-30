import pandas as pd
import numpy as np
import ta

class TechnicalAnalysis:
    def __init__(self, df):
        self.df = df.copy()
        
    def calculate_all_indicators(self):
        """Calculate all technical indicators"""
        self._calculate_moving_averages()
        self._calculate_rsi()
        self._calculate_bollinger_bands()
        self._calculate_macd()
        self._calculate_stochastic()
        self._calculate_atr()
        
        return self.df
    
    def _calculate_moving_averages(self):
        """Calculate moving averages"""
        self.df['MA_9'] = ta.trend.sma_indicator(self.df['close'], window=9)
        self.df['MA_21'] = ta.trend.sma_indicator(self.df['close'], window=21)
        self.df['MA_50'] = ta.trend.sma_indicator(self.df['close'], window=50)
        self.df['EMA_12'] = ta.trend.ema_indicator(self.df['close'], window=12)
        self.df['EMA_26'] = ta.trend.ema_indicator(self.df['close'], window=26)
        
    def _calculate_rsi(self):
        """Calculate RSI"""
        self.df['RSI'] = ta.momentum.rsi(self.df['close'], window=14)
        self.df['RSI_oversold'] = self.df['RSI'] < 30
        self.df['RSI_overbought'] = self.df['RSI'] > 70
        
    def _calculate_bollinger_bands(self):
        """Calculate Bollinger Bands"""
        bb = ta.volatility.BollingerBands(
            self.df['close'], window=20, window_dev=2
        )
        self.df['BB_upper'] = bb.bollinger_hband()
        self.df['BB_middle'] = bb.bollinger_mavg()
        self.df['BB_lower'] = bb.bollinger_lband()
        self.df['BB_width'] = bb.bollinger_wband()
        self.df['BB_pct'] = (self.df['close'] - self.df['BB_lower']) / (
            self.df['BB_upper'] - self.df['BB_lower']
        )
        
    def _calculate_macd(self):
        """Calculate MACD"""
        macd = ta.trend.MACD(self.df['close'])
        self.df['MACD'] = macd.macd()
        self.df['MACD_signal'] = macd.macd_signal()
        self.df['MACD_diff'] = macd.macd_diff()
        self.df['MACD_cross'] = self.df['MACD'] > self.df['MACD_signal']
        
    def _calculate_stochastic(self):
        """Calculate Stochastic Oscillator"""
        stoch = ta.momentum.StochasticOscillator(
            high=self.df['high'],
            low=self.df['low'],
            close=self.df['close'],
            window=14,
            smooth_window=3
        )
        self.df['STOCH_K'] = stoch.stoch()
        self.df['STOCH_D'] = stoch.stoch_signal()
        
    def _calculate_atr(self):
        """Calculate Average True Range"""
        self.df['ATR'] = ta.volatility.average_true_range(
            self.df['high'], self.df['low'], self.df['close'], window=14
        )