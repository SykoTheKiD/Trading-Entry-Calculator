#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' My personal swing trading entry formula
'''

import urllib.request
import argparse
import datetime
import holidays
import json
import sys
import ssl

API_KEY = 'ZU1OCRW90EFV4XYM'
CURRENT_CAPITAL = 7000
COMMISSION_COST = 20


class Stock:
    '''
    Holds one candlestick
    '''
    def __init__(self, high, low, close, open_price, symbol):
        self.high = high
        self.low = low
        self.close = close
        self.open_price = open_price
        self.symbol = symbol.upper()


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

def line_break(length):
    print('*' * length)

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
    break_even_price = round(entry + COMMISSION_COST / pos_size, 2)
    break_even_differential = round(break_even_price - entry, 2)
    profit_r2 = round(r2 * pos_size, 2)

    trade = Trade(stock, pos_size, entry, stop, {1: round(entry+r1, 2), 15: r15_exit, 2: r2_exit, 3: r3_exit})
    return f'''
        SYMBOL: {stock.symbol}

        Capital Risk: {cap}
        Entry: {trade.entry}
        Stop Loss: {trade.stop}
        Position Size: {trade.position_size} shares
        B/E Price: {break_even_price} -> +{break_even_differential}
        1R: {r1} -> {trade.targets[1]}
        1.5R: {r15} -> {trade.targets[15]}
        2R: {r2} -> {trade.targets[2]}
        3R: {r3} -> {trade.targets[3]}
        Potential Profit: {profit_r2}
    ''', trade

def get_last_trading_day():
    now = datetime.datetime.now()
    ## If current day is a weekend move back current day to closest previous trading day
    us_holidays = holidays.UnitedStates()
    while(5 <= now.weekday() <= 6 and now.weekday() in us_holidays):
        now = now - datetime.timedelta(days=1)

    time = now.time()
    if(datetime.datetime.now() == now and time.hour <=9 and time.minute < 30):
        now = now - datetime.timedelta(days=1)

    return now

def grab_prices(symbol):
    '''
    Get the current price for a given symbol
    '''


    with urllib.request.urlopen(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}", context=ssl.SSLContext()) as url:
        data = json.loads(url.read().decode())

    try:
        current_prices = data['Global Quote']
    except KeyError as e:
        raise KeyError("JSON Data Error")
    now = get_last_trading_day()
    today = now.strftime("%Y-%m-%d")

    if(current_prices['07. latest trading day'] != today):
        print(current_prices['07. latest trading day'])
        raise ValueError('Data for {0} is not available'.format(today))

    high = float(current_prices['03. high'])
    low = float(current_prices['04. low'])
    open_price = float(current_prices['02. open'])
    close_price = float(current_prices['05. price'])
    return Stock(high, low, close_price, open_price, symbol)


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
        print(f'''
    Stock List Summary
    *******************
    Number of Stocks: {num_trades}
    Total Potential Profit: {0.01*CURRENT_CAPITAL*2*num_trades}
    Total Potential Loss: {0.01*CURRENT_CAPITAL*num_trades}
    Lowest Price Stock: {lowest.symbol} @ {lowest.close}/shr
    Highest Price Stock: {highest.symbol} @ {highest.close}/shr
        ''')
    except AttributeError:
        print("Summary Failed")
        return -1

    total_capital_reqd = 0
    for trade in trades:
        total_capital_reqd = total_capital_reqd + (trade.entry * trade.position_size)

    msg = str()
    if(num_trades > 5):
        msg += "**Warning: Total capital at risk exceeds 5%\n**"
    if total_capital_reqd > CURRENT_CAPITAL:
        msg += f"***! Total capital required (${round(total_capital_reqd, 2)}) exceeds current capital (${CURRENT_CAPITAL}) !***"

    print(f'''
Trade Summary
***************
Total Capital Needed: ${round(total_capital_reqd, 2)}
Total Number of Trades: {num_trades}

{msg}
    ''')


def main(symbols):
    trades = []
    for symbol in symbols:
        try:
            stock = grab_prices(symbol)
            line_break(50)
            entry_calcs, trade_obj = calc(stock)
            print(entry_calcs)
            trades.append(trade_obj)

        except (ValueError, KeyError) as e:
            print("Process Error for stock", symbol.upper(), e)

    line_break(50)
    summarize(trades)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stock Symbols')
    parser.add_argument('symbols', nargs='+', type=str)
    args = parser.parse_args()
    main(args.symbols)

