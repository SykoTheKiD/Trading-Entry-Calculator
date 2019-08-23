#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' My personal swing trading entry formula
'''

import urllib.request, json
import argparse
import datetime
import sys

API_KEY = 'ZU1OCRW90EFV4XYM'
CURRENT_CAPITAL = 7000

class Stock:
    '''
    Holds one candlestick
    '''
    def __init__(self, high, low, close, open_price, symbol):
        self.high = high
        self.low = low
        self.close = close
        self.open_price = open_price
        self.symbol = symbol

class Trade:
    '''
    Holds the calculated entry and exit for a trade
    '''
    def __init__(self, stock, position_size, entry, stop, targets):
        self.stock = stock
        self.position_size = position_size
        self.entry = entry
        self.stop = stop
        self.targets = targets

def get_entry(close):
    '''
    Calculate how far above and below to place your entry/stop
    '''
    if close < 5:
        return 0.01
    elif 5 <= close < 10:
        return 0.02
    elif 10 <= close < 50:
        return 0.03
    elif 50 <= close < 100:
        return 0.05
    else:
        return 0.1

def calc(stock, capital=CURRENT_CAPITAL):
    '''
    Calculate the entry, stop and exit prices for a given stock
    '''
    if(stock.low > stock.high):
        raise ValueError('Low > High')
    if(not (stock.low <= stock.close <= stock.high)):
        raise ValueError('Low < Close < High not met', high, low, close)

    cap = round(capital * 0.01, 2)
    entry = round(stock.high + get_entry(stock.close), 2)
    stop = round(stock.low - get_entry(stock.close), 2)
    r1 = round(entry - stop, 2)
    r15 = round(r1 * 1.5, 2)
    r2 = round(r1 * 2, 2)
    r3 = round(r1 * 2.5, 2)
    r2_exit = round(entry + r2, 2)
    r15_exit = round(entry + r15, 2)
    r3_exit = round(entry + r3, 2)
    pos_size = round(cap/r1)

    profit_r2 = r2 * pos_size

    return '''
    SYMBOL: {12}

    Capital Risk: {0}
    Entry: {1}
    Stop Loss: {2}
    Position Size: {10} shares
    1R: {3} -> {13}
    1.5R: {4} -> {8}
    2R: {5} -> {7}
    3R: {6} -> {9}
    Potential Profit: {11}
    '''.format(cap,
            entry,
            stop,
            r1,
            r15,
            r2,
            r3,
            r2_exit,
            r15_exit,
            r3_exit,
            pos_size,
            profit_r2,
            stock.symbol,
            entry+r1), Trade(stock, pos_size, entry, stop, {1: entry+r1, 2: r2_exit, 3: r3_exit})

def grab_prices(symbol):
    '''
    Get the current price for a given symbol
    '''

    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")

    with urllib.request.urlopen(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}") as url:
        data = json.loads(url.read().decode())

    try:
        current_prices = data['Global Quote']
    except KeyError as e:
        raise KeyError("JSON Data Error")

    if(current_prices['07. latest trading day'] != today):
        raise ValueError('Data for {0} is not available'.format(today))

    high = float(current_prices['03. high'])
    low = float(current_prices['04. low'])
    open_price = float(current_prices['02. open'])
    close_price = float(current_prices['05. price'])
    return Stock(high, low, close_price, open_price, symbol.upper())

def summarize(trades):
    '''
    Summarize the trades and the costs
    '''
    num_trades = len(trades)
    lowest_price, highest_price = sys.maxsize, -sys.maxsize
    lowest, highest = None, None
    for trade in trades:
        cur_stock = trade.stock
        cur_price = cur_stock.close

        if cur_price < lowest_price:
            lowest = cur_stock
            lowest_price = cur_price

        if cur_price > highest_price:
            highest = cur_stock
            highest_price = cur_price
    try:
        print('''
        Stock List Summary
        *******************
        Number of Stocks: {0}
        Total Potential Profit: {1}
        Total Potential Loss: {6}
        Lowest Price Stock: {2} @ {3}/shr
        Highest Price Stock: {4} @ {5}/shr
        '''.format(num_trades,
            0.01*CURRENT_CAPITAL*2*num_trades,
            lowest.symbol,
            lowest.close,
            highest.symbol,
            highest.close,
            0.01*CURRENT_CAPITAL*num_trades
        ))
    except AttributeError as e:
        pass

    total_capital_reqd = 0
    for trade in trades:
        total_capital_reqd = total_capital_reqd + (trade.entry * trade.position_size)

    msg = str()
    if(num_trades > 5):
        msg = "Warning: Total capital at risk exceeds 5%"

    print('''
    Trade Summary
    ***************
    Total Capital Needed: ${0}
    Total Number of Trades: {1}

    {2}
    '''.format(round(total_capital_reqd, 2) , num_trades, msg))


def main(symbols):
    trades = []
    for symbol in symbols:
        try:
            stock = grab_prices(symbol)
            print('*' * 50)
            entry_calcs, trade_obj = calc(stock)
            print(entry_calcs)
            trades.append(trade_obj)

        except (ValueError, KeyError) as e:
            print("Process Error for stock", symbol.upper(), e)

    summarize(trades)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stock Symbol')
    parser.add_argument('symbols', nargs='+', type=str)
    args = parser.parse_args()
    main(args.symbols)

