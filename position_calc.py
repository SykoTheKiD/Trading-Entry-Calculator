import argparse
import datetime
from pprint import pprint
import urllib.request, json

CURRENT_CAPITAL = 7000
API_KEY = 'ZU1OCRW90EFV4XYM'

def get_entry(close):
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

def calc(high, low, close, symbol, capital=CURRENT_CAPITAL):
    if(low > high):
        raise ValueException('Low > High')
    if(not (low < close < high)):
        raise ValueException('Invalid inputs')

    cap = capital * 0.01
    entry = high + get_entry(close)
    stop = low - get_entry(close)
    r1 = entry - stop
    r15 = r1 * 1.5
    r2 = r1 * 2
    r3 = r1 * 2.5
    r2_exit = close + r2
    r15_exit = close + r15
    r3_exit = close + r3
    pos_size = cap/r1

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
    '''.format(round(cap, 2),
            round(entry, 2),
            round(stop, 2),
            round(r1, 2),
            round(r15, 2),
            round(r2, 2),
            round(r3, 2),
            round(r2_exit, 2),
            round(r15_exit, 2),
            round(r3_exit, 2),
            round(pos_size),
            round(profit_r2, 2),
            symbol.upper(),
            round(entry+r1, 2))

def grab_prices(symbol):
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")

    with urllib.request.urlopen(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}") as url:
        data = json.loads(url.read().decode())

    current_prices = data['Global Quote']

    if(current_prices['07. latest trading day'] != today):
        raise Exception('Data for {0} is not available'.format(today))

    high = float(current_prices['03. high'])
    low = float(current_prices['04. low'])
    open_price = float(current_prices['02. open'])
    close_price = float(current_prices['05. price'])

    return high, low, open_price, close_price

def main(symbols):
    for symbol in symbols:
        try:
            high, low, open_price, close = grab_prices(symbol)
        except Exception as e:
            print(symbol, e)

        print('*'*50)
        print(calc(high, low, close, symbol))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stock Symbol')
    parser.add_argument('symbols', nargs='+', type=str)
    args = parser.parse_args()
    main(args.symbols)

