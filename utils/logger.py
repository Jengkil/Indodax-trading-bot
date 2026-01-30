import logging
from datetime import datetime

class TradingLogger:
    def __init__(self, log_file='trading_log.log'):
        self.logger = logging.getLogger('TradingBot')
        self.logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        
    def log_trade(self, action, pair, price, amount):
        message = f"{action} {amount} {pair} at {price}"
        self.logger.info(message)
        
    def log_signal(self, signal, indicators):
        message = f"Signal: {signal} | RSI: {indicators.get('rsi', 0):.2f} | MACD: {indicators.get('macd', 0):.6f}"
        self.logger.info(message)
        
    def log_error(self, error_message):
        self.logger.error(error_message)