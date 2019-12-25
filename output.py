# TODO Format file

import sys
import os

CURRENT_CAPITAL = 7000 ## os.getenv['CURRENT_CAPITAL']

def line_break(length=50):
    print('*' * length)

# TODO: Add number formatting
def _clean_number(number):
    return round(number, 2)

def clean_boolean(bool):
    if bool: return "PASS"
    else: return "FAIL"

def print_swing_report(trades):
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
        total_capital_reqd = total_capital_reqd + \
            (trade.entry * trade.position_size)

    msg = str()
    if(num_trades > 5):
        msg += "**Warning: Total capital at risk exceeds 5%\n**"
    if total_capital_reqd > CURRENT_CAPITAL:
        msg += f"***! Total capital required (${_clean_number(total_capital_reqd)}) exceeds current capital (${CURRENT_CAPITAL}) !***"

    print(f'''
Trade Summary
***************
Total Capital Needed: ${_clean_number(total_capital_reqd)}
Total Number of Trades: {num_trades}

{msg}
    ''')


def print_swing_trade(stock, capital_at_risk, trade, delta_1r, delta_15r,delta_2r, delta_3r, profit_r2, break_even_price, break_even_differential):
    print(f'''
        SYMBOL: {stock.symbol}

        Capital Risk: {_clean_number(capital_at_risk)}
        Entry: {_clean_number(trade.entry)}
        Stop Loss: {_clean_number(trade.stop)}
        Position Size: {trade.position_size} shares
        B/E Price: {_clean_number(break_even_price)} -> +{_clean_number(break_even_differential)}
        1R: {_clean_number(delta_1r)} -> {_clean_number(trade.targets[1])}
        1.5R: {_clean_number(delta_15r)} -> {_clean_number(trade.targets[15])}
        2R: {_clean_number(delta_2r)} -> {_clean_number(trade.targets[2])}
        3R: {_clean_number(delta_3r)} -> {_clean_number(trade.targets[3])}
        Potential Profit: {_clean_number(profit_r2)}
    ''')


def display_intrinsic_value(results):
    print(f'''
        Company: {results["Company"]}
        Symbol: {results["Symbol"]}
        Total Debt: ${results["Total Debt"]:,}
        Total Cash on Hand: ${results["Total Cash on Hand"]:,}
        EPS 5Y: {results["EPS 5Y"]*100}%
        Projected Growth after 5Y: {results["Projected Growth"] * 100}%
        Projections using Cash flow from Operations:
                Cash Flow from Ops: ${results["Cash Flow From Ops Calculations"]["Cash Flow from Ops"]:,}
                Intrinsic Value: --> ${_clean_number(results["Cash Flow From Ops Calculations"]["Intrinsic Value"]["Intrinsic Value"])} <--
                Delta: {_clean_number(results["Evaluation"]["Delta (Cash Flow)"])}
        Projections using Net Income:
                Net Income: ${results["Net Income Calculations"]["Net Income"]:,}
                Intrinsic Value: --> ${_clean_number(results["Net Income Calculations"]["Intrinsic Value"]["Intrinsic Value"])} <--
                Delta: {_clean_number(results["Evaluation"]["Delta (Net Income)"])}
        Current PEG Ratio: {results["Evaluation"]["PEG"]}
    ''')
