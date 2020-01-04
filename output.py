# TODO Format file
from dotenv import load_dotenv
import sys
import os

load_dotenv()

CURRENT_CAPITAL = float(os.environ['CURRENT_CAPITAL'])

def line_break(length=50):
    print('*' * length)

# TODO: Add number formatting
def _clean_number(number):
    return round(number, 2)

def clean_boolean(bool):
    if bool: return "PASS"
    else: return "FAIL"

def clean_list(lst, years):
    if len(lst) >= 5 and len(years) >= 5:
        ret =f'''{years[0]} -> {lst[0]}, {years[1]} -> {lst[1]}, {years[2]} -> {lst[2]}, {years[3]} -> {lst[3]}, {years[4]} -> {lst[4]}'''
        return ret

def loading_message(msg):
    if os.getenv("VERBOSITY") == 1:
        print(msg, "...")

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


def print_intrinsic_value(results, IVCKeys):
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
                Delta (Cash Flow): {_clean_number(results[IVCKeys.evaluation.value][IVCKeys.market_delta_cash_flow.value])}
        Projections using Net Income:
                Net Income: ${results[IVCKeys.net_income_calcs.value][IVCKeys.net_income.value]:,}
                Intrinsic Value: --> ${_clean_number(results[IVCKeys.net_income_calcs.value][IVCKeys.intrinsic_value.value][IVCKeys.intrinsic_value.value])} <--
                Delta (Net Income): {_clean_number(results[IVCKeys.evaluation.value][IVCKeys.market_delta_net_income.value])}
        Current PEG Ratio: {results[IVCKeys.evaluation.value][IVCKeys.peg.value]}
        Cash Flows from Ops Increasing: {results[IVCKeys.evaluation.value][IVCKeys.cash_from_ops.value]}
        Net Incomes Increasing: {results[IVCKeys.evaluation.value][IVCKeys.net_income.value]}
    ''')


def print_value_investing_report(results, VIKeys):
    print(f''' 
        -- Value Investing Report (Details Cover (Last 5Y)) --
        Company: {results[VIKeys.company_name.value]}
        Symbol: {results[VIKeys.symbol.value]}\n
        Cash Flows From Financing: {clean_list(results[VIKeys. cash_flow_from_financing.value], results[VIKeys.years.value])}
        Cash Flows From Investing: {clean_list(results[VIKeys. cash_flow_from_investing.value], results[VIKeys.years.value])}\n
        Free Cash Flows: {clean_list([*map(lambda x: x/1e6, results[VIKeys.free_cash_flow.value])], results[VIKeys.years.value])}
        Free Cash Flow Trend: {clean_boolean(results[VIKeys.free_cash_flow_trend.value])}\n
        Debt to Equity Ratios: {clean_list([*map(_clean_number, results[VIKeys.debt_to_equity_ratio.value])], results[VIKeys.years.value])}
        Debt to Equity Ratio Trend: {clean_boolean(results[VIKeys.debt_to_equity_ratio_trend.value])}\n
        Debt Servicing Ratio (FCF): {results[VIKeys.debt_servicing_ratio_free_cash_flow_decision.value][0]}
        Debt Servicing Ratio (Net Income): {results[VIKeys.debt_servicing_ratio_net_incomes_decision.value][0]}\n
        Cash Flow from Ops: {clean_list([*map(lambda x: x/1e6, results[VIKeys.cash_flow_from_ops.value])], results[VIKeys.years.value])}
        Cash Flow from Ops Trend: {clean_boolean(results[VIKeys.cash_flow_from_ops_trend.value])}\n
        EPS: {clean_list(results[VIKeys.eps.value], results[VIKeys.years.value])}
        EPS Trend: {clean_boolean(results[VIKeys.eps_trend.value])}\n
        Net Incomes: {clean_list([*map(lambda x: x/1e6, results[VIKeys.net_incomes.value])], results[VIKeys.years.value])}
        Net Incomes Trend: {clean_boolean(results[VIKeys.net_incomes_trend.value])}\n
        Revenues: {clean_list([*map(lambda x: x/1e6, results[VIKeys.revenues.value])], results[VIKeys.years.value])}
        Revenues Trend: {clean_boolean(results[VIKeys.revenues_trend.value])}\n
        Gross Margin: {clean_list([*map(_clean_number, results[VIKeys.gross_margin.value])], results[VIKeys.years.value])}
        Gross Margin Trend: {clean_boolean(results[VIKeys.gross_margin_trend.value])}\n
        Net Profit Margin: {clean_list([*map(_clean_number, results[VIKeys.net_profit_margin.value])], results[VIKeys.years.value])}
        Net Profit Margin Trend: {clean_boolean(results[VIKeys.net_profit_margin_trend.value])}\n
        PEG Ratio: {results[VIKeys.peg_ratio.value]}
        PEG Ratio Check: {clean_boolean(results[VIKeys.peg_ratio_check.value])}\n
    ''')
