import time
import schedule
import pandas as pd
from datetime import datetime
from config.config import Config
from exchange.indodax_api import IndodaxAPI
from indicators.technical_analysis import TechnicalAnalysis
from indicators.signal_generator import SignalGenerator
from strategies.scalping_strategy import ScalpingStrategy
from database.db_handler import DatabaseHandler
from utils.logger import TradingLogger
from utils.helpers import sleep_until_next_candle

class TradingBot:
    def __init__(self):
        self.config = Config()
        api_keys = self.config.get_api_keys()
        self.api = IndodaxAPI(api_keys['api_key'], api_keys['secret_key'])
        self.db = DatabaseHandler()
        self.logger = TradingLogger()
        self.strategy = ScalpingStrategy(self.config)
        self.running = True
        
        # Initial balance
        self.balance = self.config.config.get('initial_balance', 1000000)
        
    def fetch_market_data(self):
        """Fetch OHLCV data from Indodax"""
        try:
            # Convert timeframe to seconds
            timeframe_seconds = int(self.config.timeframe[:-1]) * 60
            
            # Get OHLCV data
            ohlcv_data = self.api.get_ohlcv(
                self.config.pair,
                interval=timeframe_seconds,
                limit=100
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv_data)
            df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            
            return df
            
        except Exception as e:
            self.logger.log_error(f"Error fetching market data: {e}")
            return None
    
    def analyze_market(self, df):
        """Perform technical analysis"""
        try:
            # Calculate indicators
            ta = TechnicalAnalysis(df)
            df_with_indicators = ta.calculate_all_indicators()
            
            # Generate signals
            sg = SignalGenerator(df_with_indicators)
            signal = sg.generate_signals()
            
            # Get latest indicators for logging
            latest_indicators = {
                'rsi': df_with_indicators['RSI'].iloc[-1],
                'macd': df_with_indicators['MACD'].iloc[-1],
                'ma_9': df_with_indicators['MA_9'].iloc[-1],
                'ma_21': df_with_indicators['MA_21'].iloc[-1]
            }
            
            return signal, latest_indicators, df_with_indicators
            
        except Exception as e:
            self.logger.log_error(f"Error in market analysis: {e}")
            return 'HOLD', {}, df
    
    def execute_trading_cycle(self):
        """Execute one complete trading cycle"""
        try:
            # 1. Fetch market data
            df = self.fetch_market_data()
            if df is None or df.empty:
                return
                
            # 2. Analyze market
            signal, indicators, df_analyzed = self.analyze_market(df)
            
            # 3. Get current price
            ticker = self.api.get_ticker(self.config.pair)
            current_price = float(ticker['ticker']['last'])
            
            # 4. Execute strategy
            action, amount = self.strategy.execute_strategy(
                signal, current_price, self.balance
            )
            
            # 5. Execute trade if needed
            if action in ['BUY', 'SELL'] and amount > 0:
                if self.config.test_mode:
                    # Paper trading
                    if action == 'BUY':
                        cost = current_price * amount
                        if cost <= self.balance:
                            self.balance -= cost
                            self.logger.log_trade(
                                f"[PAPER] {action}",
                                self.config.pair,
                                current_price,
                                amount
                            )
                    elif action == 'SELL':
                        revenue = current_price * amount
                        self.balance += revenue
                        self.logger.log_trade(
                            f"[PAPER] {action}",
                            self.config.pair,
                            current_price,
                            amount
                        )
                else:
                    # Real trading
                    response = self.api.place_order(
                        self.config.pair,
                        action.lower(),
                        current_price,
                        amount
                    )
                    if response.get('success') == 1:
                        self.logger.log_trade(
                            action, self.config.pair, current_price, amount
                        )
                        
                        # Update balance
                        balance_info = self.api.get_balance()
                        # Parse balance info based on Indodax response
                        
                # Log to database
                self.db.log_trade(
                    self.config.pair,
                    action,
                    current_price,
                    amount,
                    signal,
                    self.balance
                )
            
            # 6. Log market data
            latest_candle = df_analyzed.iloc[-1].to_dict()
            self.db.log_market_data(
                self.config.pair,
                {
                    't': int(time.time() * 1000),
                    'o': latest_candle['open'],
                    'h': latest_candle['high'],
                    'l': latest_candle['low'],
                    'c': latest_candle['close'],
                    'v': latest_candle['volume']
                },
                indicators
            )
            
            # 7. Log signal
            self.logger.log_signal(signal, indicators)
            
            # 8. Log current status
            print(f"\n{'='*50}")
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Pair: {self.config.pair}")
            print(f"Price: {current_price:,.0f} IDR")
            print(f"Signal: {signal}")
            print(f"Action: {action}")
            print(f"Balance: {self.balance:,.0f} IDR")
            print(f"RSI: {indicators.get('rsi', 0):.2f}")
            print(f"MACD: {indicators.get('macd', 0):.6f}")
            print(f"{'='*50}\n")
            
        except Exception as e:
            self.logger.log_error(f"Error in trading cycle: {e}")
    
    def run(self):
        """Main bot loop"""
        self.logger.logger.info("Starting Trading Bot...")
        
        # Calculate timeframe in minutes
        timeframe_minutes = int(self.config.timeframe[:-1])
        
        while self.running:
            try:
                # Execute trading cycle
                self.execute_trading_cycle()
                
                # Sleep until next candle
                sleep_until_next_candle(timeframe_minutes)
                
            except KeyboardInterrupt:
                self.logger.logger.info("Bot stopped by user")
                self.running = False
                break
            except Exception as e:
                self.logger.log_error(f"Unexpected error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def stop(self):
        """Stop the bot"""
        self.running = False

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()