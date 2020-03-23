#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Formats outputs to the Terminal
"""

import sys

import config_loader as cl
from stock import Stock
from trade import Trade
from decorators import write_to_file

TITLE_LENGTH: int = 45
WRITE_TO_FILE: bool = False


def line_break(length=50) -> None:
    print('*' * length)


def _clean_number(number: float) -> float:
    return round(number, 2)


def clean_boolean(boolean: bool) -> str:
    return "Increasing" if boolean else "Decreasing"


def clean_list(lst: list, years: list) -> str:
    ret = ""
    len_lst = len(lst)
    if len_lst == len(years):
        for i in range(len_lst):
            ret += f"{years[i]} -> {lst[i]}, "
    return ret


def loading_message(msg: str) -> None:
    if cl.VERBOSITY == 1:
        print(msg, "...")


def log_verbose(msg: str) -> None:
    if cl.VERBOSITY == 1:
        print(msg)


def log_error(msg: Exception) -> None:
    if cl.VERBOSITY == 1:
        print("ERROR:", msg)


def print_title_panel(title: str) -> None:
    print("=" * TITLE_LENGTH)
    print("\t" + title)
    print("=" * TITLE_LENGTH)


def clean_large_values(values: list) -> list:
    return [*map(lambda x: f"${x / 1e6:,}0", values)]


def clean_numbers_in_list(lst: list) -> list:
    return [*map(_clean_number, lst)]


def check_single_bool_test(peg_ratio_bool: bool) -> str:
    return "PASS" if peg_ratio_bool else "FAIL"

@write_to_file("swing-trade-report")
def print_swing_report(trades: list) -> None:
    """
    Summarize the trades and the costs
    """
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
    Total Potential Profit: {0.01 * cl.CURRENT_CAPITAL * 2 * num_trades}
    Total Potential Loss: {0.01 * cl.CURRENT_CAPITAL * num_trades}
    Lowest Price Stock: {lowest.symbol} @ {lowest.close}/shr
    Highest Price Stock: {highest.symbol} @ {highest.close}/shr
        ''')
    except AttributeError:
        print("Summary Failed")

    total_capital_required = 0
    for trade in trades:
        total_capital_required = total_capital_required + \
                                 (trade.entry * trade.position_size)

    msg = str()
    if num_trades > 5:
        msg += "**Warning: Total capital at risk exceeds 5%\n**"
    if total_capital_required > cl.CURRENT_CAPITAL:
        msg += f"***! Total capital required (${_clean_number(total_capital_required)}) " \
               f"exceeds current capital (${cl.CURRENT_CAPITAL}) !***"

    print(f'''
Trade Summary
***************
Total Capital Needed: ${_clean_number(total_capital_required)}
Total Number of Trades: {num_trades}

{msg}
    ''')

@write_to_file("swing-trade")
def print_swing_trade(stock: Stock, capital_at_risk: int, trade: Trade, delta_1r: int, delta_15r: int, delta_2r: int,
                      delta_3r: int, profit_r2: int,
                      break_even_price: int, break_even_differential: int) -> None:
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


def format_to_percent(lst: list) -> list:
    return [*map(lambda x: str(round(x * 100, 2)) + "%", lst)]


def print_intrinsic_value(results: dict, ivc_keys) -> None:
    print_title_panel("Intrinsic Value Report")
    print(f'''
        Company: {results[ivc_keys.company_name.value]}
        Symbol: {results[ivc_keys.symbol.value]}
        Total Debt: ${results[ivc_keys.total_debt.value]:,}
        Total Cash on Hand: ${results[ivc_keys.total_cash.value]:,}
        EPS 5Y: {results[ivc_keys.eps_5Y.value] * 100}%
        Projected Growth after 5Y: {results[ivc_keys.projected_growth.value] * 100}%
        Current Market Price: --> ${results[ivc_keys.evaluation.value][ivc_keys.market_price.value]} <--
        Projections using Cash flow from Operations:
                Cash Flow from Ops: ${results[ivc_keys.cash_from_ops_calcs.value][ivc_keys.cash_from_ops.value]:,}
                Intrinsic Value: --> ${_clean_number(
        results[ivc_keys.cash_from_ops_calcs.value][
            ivc_keys.intrinsic_value.value][ivc_keys.intrinsic_value.value])} <-- 
                Delta (Cash Flow): {_clean_number(
        results[ivc_keys.evaluation.value][ivc_keys.market_delta_cash_flow.value])}
        Projections using Net Income:
                Net Income: ${results[ivc_keys.net_income_calcs.value][ivc_keys.net_income.value]:,}
                Intrinsic Value: --> ${_clean_number(
        results[ivc_keys.net_income_calcs.value][ivc_keys.intrinsic_value.value][ivc_keys.intrinsic_value.value])} <--
                Delta (Net Income): {_clean_number(
        results[ivc_keys.evaluation.value][ivc_keys.market_delta_net_income.value])}
        Current PEG Ratio: {results[ivc_keys.evaluation.value][ivc_keys.peg.value]}
        Cash Flows from Ops Increasing: {results[ivc_keys.evaluation.value][ivc_keys.cash_from_ops.value]}
        Net Incomes Increasing: {results[ivc_keys.evaluation.value][ivc_keys.net_income.value]}
    ''')


@write_to_file("value-investing-report")
def print_value_investing_report(results: dict, vi_keys) -> None:
    print_title_panel("Value Investing Report")
    print(f''' 
        -- Value Investing Report --
        Company: {results[vi_keys.company_name.value]}
        Symbol: {results[vi_keys.symbol.value]}

        --------------------
        Check if increasing
        --------------------
        Revenues: {clean_list(clean_large_values(results[vi_keys.revenues.value]), results[vi_keys.years.value])}
        Revenues Trend: {clean_boolean(results[vi_keys.revenues_trend.value])}

        Net Incomes: {clean_list(clean_large_values(results[vi_keys.net_incomes.value]), results[vi_keys.years.value])}
        Net Incomes Trend: {clean_boolean(results[vi_keys.net_incomes_trend.value])}

        Cash Flow from Ops: {clean_list(clean_large_values(results[vi_keys.cash_flow_from_ops.value]), results[vi_keys.years.value])}
        Cash Flow from Ops Trend: {clean_boolean(results[vi_keys.cash_flow_from_ops_trend.value])}

        ------------------------------------------------------------
        Check if consistent or growing and around 12-15% or higher
        ------------------------------------------------------------
        Return on Equity (Cash Flows): {clean_list(format_to_percent(clean_numbers_in_list(results[vi_keys.return_on_equity_fcf.value])), results[vi_keys.years.value])}

        Return on Equity (Net Incomes): {clean_list(format_to_percent(clean_numbers_in_list(results[vi_keys.return_on_equity_net_income.value])), results[vi_keys.years.value])}

        Return on Equity Company: {results[vi_keys.roe_company.value]}
        Return on Equity Industry: {results[vi_keys.roe_industry.value]}
        
        -----------------
        Check if above 1
        -----------------
        Current Ratio: {_clean_number(results[vi_keys.current_ratio.value])}
        Current Ratio Test: {check_single_bool_test(results[vi_keys.current_ratio_check.value])}

        -----------------------------------------------------------------
        Check if consistent or shrinking and less or equal to competitors
        -----------------------------------------------------------------
        Debt to Equity Ratios: {clean_list(format_to_percent(clean_numbers_in_list(results[vi_keys.debt_to_equity_ratio.value])), results[vi_keys.years.value])}

        Debt to Equity Company: {results[vi_keys.dtoe_company.value]}
        Debt to Equity Industry: {results[vi_keys.dtoe_industry.value]}

        -----------------------
        Check if less than 30%
        -----------------------
        Debt Servicing Ratio (FCF): {clean_list(format_to_percent(clean_numbers_in_list(results[vi_keys.debt_servicing_ratio_free_cash_flow.value])), results[vi_keys.years.value])}

        ---------------
        Check if < 1.6
        ---------------
        PEG Ratio: {results[vi_keys.peg_ratio.value]}
        PEG Ratio Check: {check_single_bool_test(results[vi_keys.peg_ratio_check.value])}

        ------------------------------------
        Check if positive and double digits
        ------------------------------------
        EPS Current Yr: {results[vi_keys.eps_current.value]}%
        EPS 1 Yr: {results[vi_keys.eps_1yr.value]}%
        EPS 5 Yr: {results[vi_keys.eps_5yr.value]}%

        -------------------------------------
        Check if margins higher than industry
        -------------------------------------
        Net Profit Margin Company: {results[vi_keys.company_npm.value]}
        Net Profit Margin Industry: {results[vi_keys.industry_npm.value]}

        -----------------
        Extra Information
        -----------------
        Cash Flows From Financing: {clean_list(results[vi_keys.cash_flow_from_financing.value], results[vi_keys.years.value])}
        Cash Flows From Investing: {clean_list(results[vi_keys.cash_flow_from_investing.value], results[vi_keys.years.value])}

        Free Cash Flows: {clean_list(clean_large_values(results[vi_keys.free_cash_flow.value]), results[vi_keys.years.value])}
        Free Cash Flow Trend: {clean_boolean(results[vi_keys.free_cash_flow_trend.value])}

        Free Cash Flows/ Revenue: {clean_list(format_to_percent(clean_numbers_in_list(results[vi_keys.free_cash_flow_revenue.value])), results[vi_keys.years.value])}

        EPS: {clean_list(results[vi_keys.eps.value], results[vi_keys.years.value])}
        EPS Trend: {clean_boolean(results[vi_keys.eps_trend.value])}

        Gross Margin: {clean_list(format_to_percent(clean_numbers_in_list(results[vi_keys.gross_margin.value])), results[vi_keys.years.value])}
        Gross Margin Trend: {clean_boolean(results[vi_keys.gross_margin_trend.value])}

        Net Profit Margin: {clean_list(format_to_percent(clean_numbers_in_list(results[vi_keys.net_profit_margin.value])), results[vi_keys.years.value])}
        Net Profit Margin Trend: {clean_boolean(results[vi_keys.net_profit_margin_trend.value])}
    ''')
