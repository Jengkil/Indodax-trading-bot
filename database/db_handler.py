import sqlite3
import pandas as pd
from datetime import datetime

class DatabaseHandler:
    def __init__(self, db_path='database/trades.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
        
    def create_tables(self):
        """Create necessary tables"""
        cursor = self.conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                pair TEXT,
                action TEXT,
                price REAL,
                amount REAL,
                total REAL,
                signal TEXT,
                profit_loss REAL,
                balance REAL
            )
        ''')
        
        # Market data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                timestamp DATETIME,
                pair TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                rsi REAL,
                macd REAL,
                PRIMARY KEY (timestamp, pair)
            )
        ''')
        
        self.conn.commit()
        
    def log_trade(self, pair, action, price, amount, signal, balance):
        """Log trade to database"""
        cursor = self.conn.cursor()
        total = price * amount
        
        cursor.execute('''
            INSERT INTO trades 
            (timestamp, pair, action, price, amount, total, signal, balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now(), pair, action, price, amount, total, signal, balance))
        
        self.conn.commit()
        
    def log_market_data(self, pair, ohlcv_data, indicators):
        """Log market data to database"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO market_data 
            (timestamp, pair, open, high, low, close, volume, rsi, macd)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.fromtimestamp(ohlcv_data['t']/1000),
            pair,
            ohlcv_data['o'],
            ohlcv_data['h'],
            ohlcv_data['l'],
            ohlcv_data['c'],
            ohlcv_data['v'],
            indicators.get('rsi', 0),
            indicators.get('macd', 0)
        ))
        
        self.conn.commit()
        
    def get_trade_history(self, limit=100):
        """Get trade history"""
        query = f"SELECT * FROM trades ORDER BY timestamp DESC LIMIT {limit}"
        return pd.read_sql_query(query, self.conn)