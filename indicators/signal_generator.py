import numpy as np

class SignalGenerator:
    def __init__(self, df):
        self.df = df
        
    def generate_signals(self):
        """Generate trading signals based on multiple indicators"""
        signals = []
        
        # Get the latest data point
        latest = self.df.iloc[-1]
        prev = self.df.iloc[-2]
        
        # 1. RSI Signal
        rsi_signal = self._check_rsi_signal(latest, prev)
        
        # 2. MACD Signal
        macd_signal = self._check_macd_signal(latest, prev)
        
        # 3. Moving Average Signal
        ma_signal = self._check_ma_signal(latest, prev)
        
        # 4. Bollinger Bands Signal
        bb_signal = self._check_bb_signal(latest)
        
        # 5. Stochastic Signal
        stoch_signal = self._check_stoch_signal(latest)
        
        # Combine signals
        buy_signals = sum([
            rsi_signal == 'BUY',
            macd_signal == 'BUY',
            ma_signal == 'BUY',
            bb_signal == 'BUY',
            stoch_signal == 'BUY'
        ])
        
        sell_signals = sum([
            rsi_signal == 'SELL',
            macd_signal == 'SELL',
            ma_signal == 'SELL',
            bb_signal == 'SELL',
            stoch_signal == 'SELL'
        ])
        
        # Decision logic
        if buy_signals >= 3 and sell_signals < 2:
            return 'BUY'
        elif sell_signals >= 3 and buy_signals < 2:
            return 'SELL'
        else:
            return 'HOLD'
    
    def _check_rsi_signal(self, latest, prev):
        if latest['RSI'] < 30 and prev['RSI'] >= 30:
            return 'BUY'
        elif latest['RSI'] > 70 and prev['RSI'] <= 70:
            return 'SELL'
        return 'HOLD'
    
    def _check_macd_signal(self, latest, prev):
        if latest['MACD_cross'] and not prev['MACD_cross']:
            return 'BUY'
        elif not latest['MACD_cross'] and prev['MACD_cross']:
            return 'SELL'
        return 'HOLD'
    
    def _check_ma_signal(self, latest, prev):
        if (latest['MA_9'] > latest['MA_21'] and 
            prev['MA_9'] <= prev['MA_21']):
            return 'BUY'
        elif (latest['MA_9'] < latest['MA_21'] and 
              prev['MA_9'] >= prev['MA_21']):
            return 'SELL'
        return 'HOLD'
    
    def _check_bb_signal(self, latest):
        if latest['close'] < latest['BB_lower']:
            return 'BUY'
        elif latest['close'] > latest['BB_upper']:
            return 'SELL'
        return 'HOLD'
    
    def _check_stoch_signal(self, latest):
        if latest['STOCH_K'] < 20 and latest['STOCH_D'] < 20:
            return 'BUY'
        elif latest['STOCH_K'] > 80 and latest['STOCH_D'] > 80:
            return 'SELL'
        return 'HOLD'