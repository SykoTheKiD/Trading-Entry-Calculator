# TODO Format file
from intrinsic_value_calculator import IVCKeys
from value_investing import VIKeys
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


def print_intrinsic_value(results):
    print(f'''
        Company: {results[IVCKeys.company_name.value]}
        Symbol: {results[IVCKeys.symbol.value]}
        Total Debt: ${results[IVCKeys.total_debt.value]:,}
        Total Cash on Hand: ${results[IVCKeys.total_cash.value]:,}
        EPS 5Y: {results[IVCKeys.eps_5Y.value]*100}%
        Projected Growth after 5Y: {results[IVCKeys.projected_growth.value] * 100}%
        Projections using Cash flow from Operations:
                Cash Flow from Ops: ${results[IVCKeys.cash_from_ops_calcs.value][IVCKeys.cash_from_ops.value]:,}
                Intrinsic Value: --> ${_clean_number(results[IVCKeys.cash_from_ops_calcs.value][IVCKeys.intrinsic_value.value][IVCKeys.intrinsic_value.value])} <--
                Delta: {_clean_number(results[IVCKeys.evaluation.value][IVCKeys.market_delta.value])}
        Projections using Net Income:
                Net Income: ${results[IVCKeys.net_income_calcs.value][IVCKeys.net_income.value]:,}
                Intrinsic Value: --> ${_clean_number(results[IVCKeys.net_income_calcs.value][IVCKeys.intrinsic_value.value][IVCKeys.intrinsic_value.value])} <--
                Delta: {_clean_number(results[IVCKeys.evaluation.value][IVCKeys.market_delta.value])}
        Current PEG Ratio: {results[IVCKeys.evaluation.value][IVCKeys.peg.value]}
        Cash Flows from Ops Increasing: {results[IVCKeys.evaluation.value][IVCKeys.cash_from_ops.value]}
        Net Incomes Increasing: {results[IVCKeys.evaluation.value][IVCKeys.net_income.value]}
    ''')


def print_value_investing_report(results):
    print(f''' 
        -- Details Cover (Last 5Y) --
        Company: {results[VIKeys.company_name.value]}
        Symbol: {results[VIKeys.symbol.value]}
        Cash Flows From Financing: {results[VIKeys. cash_flow_from_financing.value]}
        Cash Flows From Investing: {results[VIKeys. cash_flow_from_investing.value]}
        Free Cash Flows: {[*map(lambda x: x/1e6, results[VIKeys.free_cash_flow.value])]}
        Free Cash Flow Trend: {clean_boolean(results[VIKeys.free_cash_flow_trend.value])}
        Debt to Equity Ratios: {[*map(_clean_number, results[VIKeys.debt_to_equity_ratio.value])]}
        Debt to Equity Ratio Trend: {clean_boolean(results[VIKeys.debt_to_equity_ratio_trend.value])}
        Debt Servicing Ratio (FCF): {results[VIKeys.debt_servicing_ratio_free_cash_flow_decision.value]}
        Debt Servicing Ratio (Net Income): {results[VIKeys.debt_servicing_ratio_net_incomes_decision.value]}
        Cash Flow from Ops: {[*map(lambda x: x/1e6, results[VIKeys.cash_flow_from_ops.value])]}
        Cash Flow from Ops Trend: {results[VIKeys.cash_flow_from_ops_trend.value]}
        EPS: {results[VIKeys.eps.value]}
        EPS Trend: {results[VIKeys.eps_trend.value]}
        Net Incomes: {[*map(lambda x: x/1e6, results[VIKeys.net_incomes.value])]}
        Net Incomes Trend: {results[VIKeys.net_incomes_trend.value]}
        Revenues: {[*map(lambda x: x/1e6, results[VIKeys.revenues.value])]}
        Revenues Trend: {results[VIKeys.revenues_trend.value]}
        Gross Margin: {[*map(_clean_number, results[VIKeys.gross_margin.value])]}
        Gross Margin Trend: {results[VIKeys.gross_margin_trend.value]}
        Net Profit Margin: {[*map(_clean_number, results[VIKeys.net_profit_margin.value])]}
        Net Profit Margin Trend: {results[VIKeys.net_profit_margin_trend.value]}
        PEG Ratio: {results[VIKeys.peg_ratio.value]}
        PEG Ratio Check: {results[VIKeys.peg_ratio_check.value] }
    ''')
