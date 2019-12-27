import statement_retrieval as stret
from finviz import get_peg_ratio
from fuzzy import fuzzy_increase
from operator import truediv
import urllib.request
import output as op
import operator
import json

def calculate_ratios(lst1, lst2):
    return [*map(truediv, lst1, lst2)]

def calculate_ttm_ratio(lst1, lst2):
    ttm1 = lst1[-1]
    ttm2 = lst2[-1]
    return ttm1/ttm2

def calculate_debt_equity_ratios(total_liabilities, total_shareholder_equity):
    return calculate_ratios(total_liabilities, total_shareholder_equity)


def calculate_current_ratio(total_current_assets, total_current_liabilities):
    return calculate_ttm_ratio(total_current_assets, total_current_liabilities)


def calculate_debt_servicing_ratio(net_interest_expenses, cash_source):
    # net_income / cash_flow_from_ops ideally < 30%
    return calculate_ttm_ratio(net_interest_expenses, cash_source)

def calculate_fcf_revenue(free_cash_flows, revenues):
    return calculate_ratios(free_cash_flows, revenues)

def calculate_return_on_equity(cash_source, total_shareholder_equity):
    # roe = net incomes or fcf / (assets - liabilities) or total shareholders equity
    return calculate_ratios(cash_source, total_shareholder_equity)
    # consistently > 12% good
    # consistently > 50% amazing

def _calculate_flow_graph(flows, positive_bound):
    ret = []
    for i in range(len(flows)):
        if i > positive_bound:
            ret.append('+')
        else:
            ret.append('-')
    return ret

def cash_flow_financing_list(cash_froms):
    return _calculate_flow_graph(cash_froms, 0)

def is_debt_servicing_ratio_good(ds_ratios):
    return _calculate_flow_graph(ds_ratios, 0.3)

def extract_values_from_statment(statements, statement_attribute):
    float_vals = []
    try:
        for i in range(len(statements)):
            float_val = float(statements[i][statement_attribute.attribute_name])
            float_vals.append(float_val)
    except ValueError:
        print("ERROR " + statements[i][statement_attribute.attribute_name])
    return float_vals

def main(stock_list):
    if len(stock_list) == 0: return
    stocks = ','.join(symbol.upper() for symbol in stock_list)
    
    income_statements_yrly = stret.get_financial_statement(
        stret.INCOME_STATEMENT, stocks)[stret.StatementKeys.financials.value][::-1][5:]
    balance_sheets_qrtrly = stret.get_financial_statement(
        stret.BALANCE_SHEET, stocks, quarterly=True)[stret.StatementKeys.financials.value][::-1][5:]
    cash_flow_statements_yrly = stret.get_financial_statement(
        stret.CASH_FLOW_STATEMENT, stocks)[stret.StatementKeys.financials.value][::-1][5:]
    
    net_incomes = extract_values_from_statment(
        income_statements_yrly, stret.NET_INCOME_ATTR)
    revenues = extract_values_from_statment(
        income_statements_yrly, stret.REVENUE_ATTR)
    eps_diluted = extract_values_from_statment(
        income_statements_yrly, stret.EPS_DILUTED_ATTR)
    cash_flow_from_ops = extract_values_from_statment(
        cash_flow_statements_yrly, stret.CASH_FLOW_FROM_OPERATIONS_ATTR)
    total_current_assets = extract_values_from_statment(
        balance_sheets_qrtrly, stret.TOTAL_CURRENT_ASSETS_ATTR)
    total_liabilities = extract_values_from_statment(
        balance_sheets_qrtrly, stret.TOTAL_LIABILITIES_ATTR)
    total_current_liabilities = extract_values_from_statment(
        balance_sheets_qrtrly, stret.TOTAL_CURRENT_LIABILITIES_ATTR)
    total_shareholders_equity = extract_values_from_statment(
        balance_sheets_qrtrly, stret.TOTAL_SHAREHOLDER_EQUITY_ATTR)
    free_cash_flows = extract_values_from_statment(
        cash_flow_statements_yrly, stret.FREE_CASH_FLOWS_ATTR)
    cash_from_financing = extract_values_from_statment(
        cash_flow_statements_yrly, stret.CASH_FROM_FINANCING_ATTR)
    cash_from_investments = extract_values_from_statment(
        cash_flow_statements_yrly, stret.CASH_FROM_INVESTMENTS_ATTR)
    interest_expense = extract_values_from_statment(
        income_statements_yrly, stret.INTEREST_EXPENSE_ATTR)
    gross_margin = extract_values_from_statment(income_statements_yrly, stret.GROSS_MARGIN_ATTR)
    net_profit_margins = extract_values_from_statment(income_statements_yrly, stret.NET_PROFIT_MARGIN_ATTR)

    current_ratio = calculate_current_ratio(total_current_assets, total_current_liabilities)
    de_ratios = calculate_debt_equity_ratios(total_liabilities, total_shareholders_equity)
    debt_servicing_ratios  = calculate_debt_servicing_ratio(interest_expense, cash_flow_from_ops)
    fcf_revenues = calculate_fcf_revenue(free_cash_flows, revenues)
    return_on_equity_fcf = calculate_return_on_equity(free_cash_flows, total_shareholders_equity)
    return_on_equity_net_income = calculate_return_on_equity(
        net_incomes, total_shareholders_equity)

    print(cash_flow_financing_list(cash_from_investments))
    print(cash_flow_financing_list(cash_from_financing))
    print(fuzzy_increase(stret.FREE_CASH_FLOWS_ATTR, free_cash_flows))
    print(fuzzy_increase(stret.DEBT_TO_EQUITY_RATIO_ATTR, de_ratios))
    print(is_debt_servicing_ratio_good([debt_servicing_ratios]))
    print(fuzzy_increase(stret.CASH_FLOW_FROM_OPERATIONS_ATTR,cash_flow_from_ops))
    print(fuzzy_increase(stret.EPS_DILUTED_ATTR, eps_diluted))
    print(fuzzy_increase(stret.NET_INCOME_ATTR, net_incomes))
    print(fuzzy_increase(stret.REVENUE_ATTR, revenues))
    print(fuzzy_increase(stret.GROSS_MARGIN_ATTR, gross_margin))
    print(fuzzy_increase(stret.NET_PROFIT_MARGIN_ATTR, net_profit_margins))

if __name__ == "__main__":
    main(["AAPL"])

# income statement
# TODO gross profit higher than industry
# TODO net profit higher than industry
