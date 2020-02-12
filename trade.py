#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' Holds a trade and its information
'''
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

class Investment:
    def __init__(self, stock, revenue_score):
        self.stock = stock
        self.revenue_score = revenue_score
