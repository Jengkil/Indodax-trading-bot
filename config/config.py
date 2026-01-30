import json
import os

class Config:
    def __init__(self):
        with open('config/api_config.json') as f:
            self.config = json.load(f)
        
        # Trading parameters
        self.pair = self.config.get('pair', 'btc_idr')
        self.timeframe = '5m'  # 5 minutes for scalping
        self.test_mode = self.config.get('test_mode', True)
        
        # Risk Management
        self.max_position_size = 0.1  # 10% of balance per trade
        self.stop_loss = 0.02  # 2%
        self.take_profit = 0.015  # 1.5%
        self.max_daily_loss = 0.05  # 5%
        
        # Scalping parameters
        self.rsi_period = 14
        self.bb_period = 20
        self.ma_fast = 9
        self.ma_slow = 21
        
    def get_api_keys(self):
        return {
            'api_key': self.config['api_key'],
            'secret_key': self.config['secret_key']
        }