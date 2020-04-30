import pandas as pd
from math import sqrt
from pprint import pprint
class Backtester:
    def __init__(self, quotes, threshold, fee=0.0007, t_pen=500):
        self.in_position = False
        self.position = {'x': 0, 'y': 0}
        self.prices = {'x': 0, 'y': 0}
        self.balance = 1000
        self.trades = []
        self.threshold = threshold
        self.fee = fee
        self.elapsed = 0
        self.max_loss = 0
        self.max_loss_time = 0
        self.max_gain = 0
        self.max_gain_time = 0
        self.doubled_down = False
        self.t_pen = t_pen
        self.quotes = quotes
        self.backtest()
        pprint(self.get_metrics())
        
    def can_open(self, quote):
        if self.in_position and self.elapsed < self.t_pen:
            return False
        if self.doubled_down:
            return False
        if abs(quote.z) >= self.threshold:
            if self.elapsed >= self.t_pen:
                self.doubled_down = True
            return True

    
    def calc_profit(self, quote):
        return self.position['x'] * (quote.x - self.prices['x']) + self.position['y'] * (quote.y - self.prices['y'])

    def can_close(self, quote):
        if not self.in_position:
            return False
        self.elapsed += 5
        if self.calc_profit(quote) < self.max_loss:
            self.max_loss = self.calc_profit(quote)
            self.max_loss_time = self.elapsed
        elif self.calc_profit(quote) > self.max_gain:
            self.max_gain = self.calc_profit(quote)
            self.max_gain_time = self.elapsed
        self.max_gain = max(self.max_gain, self.calc_profit(quote))
        if self.position['y'] > 0 and quote.z >= 0:
            return True
        elif self.position['y'] < 0 and quote.z <= 0:
            return True
        return False

    def open(self, quote):
        new_x = 2500/quote.x
        new_y = 2500/quote.y
        self.prices['x'] = (new_x * quote.x + self.prices['x'] * abs(self.position['x']))/ (new_x + abs(self.position['x']))
        self.prices['y'] = (new_y * quote.y + self.prices['y'] * abs(self.position['y']))/ (new_y + abs(self.position['y']))
        self.in_position = True

        if quote.z <= -1 * self.threshold:
            new_x *= -1
            self.prices['x'] *= 1/quote.x_mult
            self.prices['y'] *= quote.y_mult
        else:
            new_y *= -1
            self.prices['x'] *= quote.x_mult
            self.prices['y'] *= 1/quote.y_mult
        
        self.position['x'] += new_x
        self.position['y'] += new_y
        
        self.trades.append({
            'time': quote.time,
            'type': 'open',
            'x': self.position['x'],
            'y': self.position['y'],
            'x_price': self.prices['x'],
            'y_price': self.prices['y'],
            'profit': 0,
            'balance': self.balance,
            'max_loss': 0,
            'max_gain': 0,
            'max_loss_time': 0,
            'max_gain_time': 0,
            'elapsed': self.elapsed
        })
    
    def close(self, quote):
        profit = self.calc_profit(quote) - abs(self.position['x']) * self.prices['x'] * self.fee * 4
        self.balance += profit
        self.in_position = False
        self.position = {'x': 0, 'y': 0}
        self.trades.append({
            'time': quote.time,
            'type': 'close',
            'x': self.position['x'],
            'y': self.position['y'],
            'x_price': quote.x,
            'y_price': quote.y,
            'profit': profit,
            'balance': self.balance,
            'max_loss': self.max_loss,
            'max_gain': self.max_gain,
            'max_loss_time': self.max_loss_time,
            'max_gain_time': self.max_gain_time,
            'elapsed': self.elapsed
        })
        self.num_trades = 0
        self.max_loss = 0
        self.max_gain = 0
        self.max_loss_time = 0
        self.max_gain_time = 0
        self.elapsed = 0
        self.doubled_down = False
    
    def backtest(self):
        for quote in self.quotes.itertuples():
            if self.can_close(quote):
                self.close(quote)
            if self.can_open(quote):
                self.open(quote)
            self.last_z = quote.z

    def get_metrics(self):
        returns = round((self.balance - 1000)/10,2)
        trades = pd.DataFrame(self.trades)
        trades = trades[trades.type == 'close']
        trades.set_index('time', inplace=True, drop=True)
        daily = trades.resample('1D').balance.last().pct_change().dropna()
        duration = round(len(self.quotes)/(12*24*30), 2)
        return {
            'pct_return': returns,
            'num_trades': len(trades) * 4,
            'win_rate': round(len(trades[trades.profit >= 0])/len(trades), 2),
            'sharpe': round(sqrt(365) * daily.mean()/daily.std(), 2),
            'duration ': f'{duration} months'
        }
    

