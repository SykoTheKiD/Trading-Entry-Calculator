#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' My personal swing trading entry formula
'''
from pricing import get_last_price_data, PricePayloadKeys
from dotenv import load_dotenv
from stock import Stock
from trade import Trade

import output as op
import argparse
import datetime
import holidays

import sys
import os

load_dotenv()
CURRENT_CAPITAL = float(os.environ['CURRENT_CAPITAL'])
COMMISSION_COST = float(os.environ['COMMISSION_COST'])

## TODO: Add break for large candles
def get_price_padding(closing_price):
    '''
    Calculate how far above and below to place your entry/stop
    '''
    if closing_price < 5:
        return 0.01
    elif 5 <= closing_price < 10:
        return 0.02
    elif 10 <= closing_price < 50:
        return 0.03
    elif 50 <= closing_price < 100:
        return 0.05
    else:
        return 0.1

def calculate_entry_exits(stock):
    '''
    Calculate the entry, stop and exit prices for a given stock
    '''
    high = stock.high
    low = stock.low
    close = stock.close
    if(low > high):
        raise ValueError('Low > High')
    if(not (low <= close <= high)):
        raise ValueError('Low < Close < High not met', high, low, close)

    capital_at_risk = CURRENT_CAPITAL * 0.01
    entry = high + get_price_padding(close)
    stop = low  - get_price_padding(close)
    
    delta_1r = entry - stop
    delta_15r = delta_1r * 1.5
    delta_2r = delta_1r * 2
    delta_3r = delta_1r * 2.5

    r15_exit = entry + delta_15r
    r2_exit = entry + delta_2r
    r3_exit = entry + delta_3r
    
    pos_size = round(capital_at_risk/delta_1r)
    break_even_price = entry + COMMISSION_COST / pos_size
    break_even_differential = break_even_price - entry
    profit_r2 = delta_2r * pos_size

    trade = Trade(stock, pos_size, entry, stop, {
                  1: entry+delta_1r, 15: r15_exit, 2: r2_exit, 3: r3_exit})
    op.print_swing_trade(stock, capital_at_risk, trade, delta_1r, delta_15r, delta_2r, delta_3r, profit_r2, break_even_price, break_even_differential)
    return trade

def get_last_trading_day():
    now = datetime.datetime.now()
    ## If current day is a weekend move back current day to closest previous trading day
    us_holidays = holidays.UnitedStates()
    while(5 <= now.weekday() <= 6 and now.weekday() in us_holidays):
        now = now - datetime.timedelta(days=1)

    time = now.time()
    if datetime.datetime.now() == now and time.hour <=9 and time.minute < 30:
        now = now - datetime.timedelta(days=1)

    return now

def grab_prices(symbol):
    '''
    Get the current price for a given symbol
    '''

    try:
        current_prices = get_last_price_data(symbol)
        now = get_last_trading_day()
        today = now.strftime("%Y-%m-%d")
        last_trading_day = current_prices[PricePayloadKeys.last_trading_day.value]
        if  last_trading_day != today:
            print(last_trading_day)
            raise ValueError('Data for {0} is not available'.format(today))

        high = float(current_prices[PricePayloadKeys.high.value])
        low = float(current_prices[PricePayloadKeys.low.value])
        open_price = float(current_prices[PricePayloadKeys.open_price.value])
        close_price = float(current_prices[PricePayloadKeys.price.value])
        return Stock(high, low, close_price, open_price, symbol)
    except KeyError:
        print("JSON Response from AlphaVantage Corrupt")

def main(symbols):
    trades = []
    for symbol in symbols:
        # try:
        stock = grab_prices(symbol)
        op.line_break()
        trade_obj = calculate_entry_exits(stock)
        trades.append(trade_obj)

        # except (ValueError, KeyError) as e:
            # print("Process Error for stock", symbol.upper(), e)

    op.line_break()
    op.print_swing_report(trades)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stock Symbols')
    parser.add_argument('symbols', nargs='+', type=str)
    args = parser.parse_args()
    main(args.symbols)

