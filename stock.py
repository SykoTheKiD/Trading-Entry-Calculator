#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Holds a candlestick
"""


class Stock:
    """
    Holds one candlestick
    """

    def __init__(self, high, low, close, open_price, symbol):
        self.high = high
        self.low = low
        self.close = close
        self.open_price = open_price
        self.symbol = symbol.upper()
