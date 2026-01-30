import hmac
import hashlib
import requests
import time
import json
from urllib.parse import urlencode

class IndodaxAPI:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://indodax.com"
        self.public_url = f"{self.base_url}/api"
        
    def _sign(self, data):
        return hmac.new(
            self.secret_key.encode(),
            urlencode(data).encode(),
            hashlib.sha512
        ).hexdigest()
    
    def get_ticker(self, pair):
        """Get current ticker information"""
        url = f"{self.public_url}/{pair}/ticker"
        response = requests.get(url)
        return response.json()
    
    def get_order_book(self, pair):
        """Get order book"""
        url = f"{self.public_url}/{pair}/depth"
        response = requests.get(url)
        return response.json()
    
    def get_trades(self, pair, limit=1000):
        """Get recent trades"""
        url = f"{self.public_url}/{pair}/trades"
        response = requests.get(url)
        return response.json()[:limit]
    
    def get_ohlcv(self, pair, interval=300, limit=100):
        """Get OHLCV data"""
        # Convert to minutes for Indodax API
        minutes = interval // 60
        url = f"{self.base_url}/tradingview/history?symbol={pair}&resolution={minutes}&from={int(time.time()-interval*limit)}&to={int(time.time())}"
        response = requests.get(url)
        return response.json()
    
    def private_request(self, method, params=None):
        """Make private API request"""
        if params is None:
            params = {}
        
        params['method'] = method
        params['nonce'] = int(time.time() * 1000)
        
        headers = {
            'Key': self.api_key,
            'Sign': self._sign(params)
        }
        
        response = requests.post(
            f"{self.base_url}/tapi",
            data=params,
            headers=headers
        )
        
        return response.json()
    
    def get_balance(self):
        """Get account balance"""
        return self.private_request('getInfo')
    
    def place_order(self, pair, type, price, amount):
        """Place buy/sell order"""
        params = {
            'pair': pair,
            'type': type,  # 'buy' or 'sell'
            'price': price,
            'amount': amount
        }
        return self.private_request('trade', params)
    
    def cancel_order(self, pair, order_id):
        """Cancel order"""
        params = {
            'pair': pair,
            'order_id': order_id
        }
        return self.private_request('cancelOrder', params)
    
    def get_open_orders(self, pair):
        """Get open orders"""
        params = {'pair': pair}
        return self.private_request('openOrders', params)