'''
6/18 Crossover Long Rules

-- 6 EMA croses above 18 EMA
-- MACD(12, 26, 9) is bullish
-- Candle after indicator must be swing high
-- Swing high must be followed pull back candle (pullback == lower high than swing high)
'''

def is_pullback(stock1, stock2):
    return stock1.high > stock2.high

def ema_cross():
    pass

def macd():
    pass
