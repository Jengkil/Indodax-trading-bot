class ScalpingStrategy:
    def __init__(self, config):
        self.config = config
        self.position = None
        self.entry_price = 0
        self.stop_loss = 0
        self.take_profit = 0
        
    def execute_strategy(self, signal, current_price, balance):
        """Execute scalping strategy"""
        action = 'HOLD'
        amount = 0
        
        if signal == 'BUY' and not self.position:
            # Calculate position size
            position_size = balance * self.config.max_position_size
            amount = position_size / current_price
            
            # Set stop loss and take profit
            self.stop_loss = current_price * (1 - self.config.stop_loss)
            self.take_profit = current_price * (1 + self.config.take_profit)
            
            self.position = 'LONG'
            self.entry_price = current_price
            action = 'BUY'
            
        elif self.position == 'LONG':
            # Check stop loss
            if current_price <= self.stop_loss:
                action = 'SELL'
                amount = self.position_size
                self.position = None
                
            # Check take profit
            elif current_price >= self.take_profit:
                action = 'SELL'
                amount = self.position_size
                self.position = None
                
            # Check if we should cut loss based on signal
            elif signal == 'SELL':
                action = 'SELL'
                amount = self.position_size
                self.position = None
        
        return action, amount
    
    def calculate_dynamic_stop_loss(self, atr, current_price):
        """Calculate dynamic stop loss based on ATR"""
        atr_multiplier = 1.5
        stop_loss_distance = atr * atr_multiplier
        return current_price - stop_loss_distance