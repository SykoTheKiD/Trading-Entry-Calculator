from finviz import get_peg_ratio, get_company_name, get_eps_growth
from exceptions import DocumentError, FinvizError
from operator import truediv, gt, le
import statement_retrieval as stret
from fuzzy import fuzzy_increase
from enum import Enum
import urllib.request
import output as op
import zacks_api
import operator
import json

class FlowThreshold:
    def __init__(self, operation, threshold):
        self.operation = operation
        self.threshold = threshold


DEBT_SERVICING_RATIO_THRESHOLD = FlowThreshold(le, 0.3)
CASH_FLOW_FROM_INVESTING_THRESHOLD = FlowThreshold(gt, 0)
CASH_FLOW_FROM_FINANCING_THRESHOLD = FlowThreshold(gt, 0)
class VIKeys(Enum):
    company_name = "Company Name"
    symbol = "Symbol"
    cash_flow_from_investing = "Cash Flow From Investing"
    cash_flow_from_financing = "Cash Flow From Financing"
    free_cash_flow = "Free Cash Flows"
    free_cash_flow_trend = "Free Cash Flow Trend"
    debt_to_equity_ratio = "Debt to Equity Ratio"
    debt_to_equity_ratio_trend = "Debt to Equity Ratio Trend"
    debt_servicing_ratio_free_cash_flow = "Debt Servicing Ratio (Free Cash Flows)"
    debt_servicing_ratio_free_cash_flow_decision = "Debt Servicing Ratio (FCF)Decision"
    debt_servicing_ratio_net_incomes = "Debt Servicing Ratio (Net Incomes)"
    debt_servicing_ratio_net_incomes_decision = "Debt Servicing Ratio (Net Income) Decision"
    cash_flow_from_ops = "Cash Flow From Operations"
    cash_flow_from_ops_trend = "Cash Flow From Operations Trend"
    eps = "EPS"
    eps_trend = "EPS Trend"
    net_incomes = "Net Income"
    net_incomes_trend = "Net Income Trend"
    revenues = "Revenue"
    revenues_trend = "Revenue Trend"
    gross_margin = "Gross Margin"
    gross_margin_trend = "Gross Margin Trend"
    net_profit_margin = "Net Profit Margin"
    net_profit_margin_trend = "Net Profit Margin Trend"
    peg_ratio = "PEG Ratio"
    peg_ratio_check = "PEG Ratio Check"
    years = "Years"
    current_ratio = "Current Ratio"
    current_ratio_check = "Current Ratio Check"
    free_cash_flow_revenue = "FCF Revenue"
    return_on_equity_fcf = "ROE FCF"
    return_on_equity_net_income = "ROE Net Income"
    quarters = "Quarters"
    eps_current = "EPS Current"
    eps_1yr = "EPS 1 Yr"
    eps_5yr = "EPS 5 Yr"
    company_npm = "Company NPM"
    industry_npm = "Industry NPM"
    roe_company = "ROE company"
    roe_industry = "ROE Industry"
    dtoe_company = "D to E Company"
    dtoe_industry = "D to E Industry" 

def calculate_ratios(lst1, lst2):
    return [*map(truediv, lst1, lst2)]

def calculate_ttm_ratio(lst1, lst2):
    if len(lst1) > 0 and len(lst2) > 0:
        ttm1 = lst1[-1]
        ttm2 = lst2[-1]
        return ttm1/ttm2
    return -1

def calculate_flow_graph(flows, flow_threshold):
    ret = []
    for i in range(len(flows)):
        if flow_threshold.operation(i, flow_threshold.threshold):
            ret.append('+')
        else:
            ret.append('-')
    return ret

def extract_values_from_statment(statements, statement_attribute):
    float_vals = []
    try:
        for i in range(len(statements)):
            float_val = float(statements[i][statement_attribute.attribute_name])
            float_vals.append(float_val)
        return float_vals
    except (ValueError, KeyError) as e:
        op.log_error(e)
        raise DocumentError


def evaluate_peg_ratio(peg_ratio):
    if peg_ratio == None:
        return None
    return peg_ratio <= 1.6

def main(stock):
    stock = stock.upper()
    try:
        op.loading_message("Fetching Yearly Income Statements")
        income_statements_yrly = stret.get_financial_statement(
            stret.INCOME_STATEMENT, stock)[stret.StatementKeys.financials.value][::-1][-5:]
        op.loading_message("Fetching Quarterly Balance Sheets")
        balance_sheets_qrtrly = stret.get_financial_statement(
            stret.BALANCE_SHEET, stock, quarterly=True)[stret.StatementKeys.financials.value][::-1][-5:]
        op.loading_message("Fetching Yearly Cash Flow Statements")
        cash_flow_statements_yrly = stret.get_financial_statement(
            stret.CASH_FLOW_STATEMENT, stock)[stret.StatementKeys.financials.value][::-1][-5:]
    except KeyError as e:
        op.log_error(e)
        return

    op.loading_message("Parsing Years")
    years = []
    for i in range(len(income_statements_yrly)):
        years.append(income_statements_yrly[i]['date'])
    years = [year.split('-')[0] for year in years]

    quarters = []
    for i in range(len(balance_sheets_qrtrly)):
        quarters.append(balance_sheets_qrtrly[i]['date'])

    try:
        op.loading_message("Parsing Net Incomes")
        net_incomes = extract_values_from_statment(
            income_statements_yrly, stret.NET_INCOME_ATTR)
        op.loading_message("Parsing Revenues")
        revenues = extract_values_from_statment(
            income_statements_yrly, stret.REVENUE_ATTR)
        op.loading_message("Parsing EPS Diluted")
        eps_diluted = extract_values_from_statment(
            income_statements_yrly, stret.EPS_DILUTED_ATTR)
        op.loading_message("Parsing Cash Flow from Operations")
        cash_flow_from_ops = extract_values_from_statment(
            cash_flow_statements_yrly, stret.CASH_FLOW_FROM_OPERATIONS_ATTR)
        op.loading_message("Parsing Total Current Assets")
        total_current_assets = extract_values_from_statment(
            balance_sheets_qrtrly, stret.TOTAL_CURRENT_ASSETS_ATTR)
        op.loading_message("Parsing Total Liabilities")
        total_liabilities = extract_values_from_statment(
            balance_sheets_qrtrly, stret.TOTAL_LIABILITIES_ATTR)
        op.loading_message("Parsing Total Current Liabilities")
        total_current_liabilities = extract_values_from_statment(
            balance_sheets_qrtrly, stret.TOTAL_CURRENT_LIABILITIES_ATTR)
        op.loading_message("Parsing Total Shareholder Equity")
        total_shareholders_equity = extract_values_from_statment(
            balance_sheets_qrtrly, stret.TOTAL_SHAREHOLDER_EQUITY_ATTR)
        op.loading_message("Parsing Free Cash Flows")
        free_cash_flows = extract_values_from_statment(
            cash_flow_statements_yrly, stret.FREE_CASH_FLOWS_ATTR)
        op.loading_message("Parsing Cash From Financing")
        cash_from_financing = extract_values_from_statment(
            cash_flow_statements_yrly, stret.CASH_FROM_FINANCING_ATTR)
        op.loading_message("Parsing Cash From Investments")
        cash_from_investments = extract_values_from_statment(
            cash_flow_statements_yrly, stret.CASH_FROM_INVESTMENTS_ATTR)
        op.loading_message("Parsing Interest Expense")
        interest_expense = extract_values_from_statment(
            income_statements_yrly, stret.INTEREST_EXPENSE_ATTR)
        op.loading_message("Parsing Gross Margin")
        gross_margin = extract_values_from_statment(income_statements_yrly, stret.GROSS_MARGIN_ATTR)
        op.loading_message("Parsing Net Margin")
        net_profit_margins = extract_values_from_statment(income_statements_yrly, stret.NET_PROFIT_MARGIN_ATTR)
    except DocumentError as e:
        op.log_error(e)

    op.loading_message("Calculating Current Ratio")
    current_ratio = calculate_ttm_ratio(
        total_current_assets, total_current_liabilities)
    current_ratio_check = current_ratio >= 1
    op.loading_message("Calculating Debt to Equity Ratio")
    de_ratios = calculate_ratios(total_liabilities, total_shareholders_equity)
    op.loading_message("Calculating Debt Servicing Ratio")
    debt_servicing_ratios_fcf = calculate_ratios(
        interest_expense, free_cash_flows)
    op.loading_message("Calculating Free Cash Flow (Revenues)")
    fcf_revenues = calculate_ratios(free_cash_flows, revenues)
    op.loading_message("Calculating Return on Equity (FCF)")
    return_on_equity_fcf = calculate_ratios(
        free_cash_flows, total_shareholders_equity)
    op.loading_message("Calculating Return on Equity (Net Income)")
    return_on_equity_net_income = calculate_ratios(
        net_incomes, total_shareholders_equity)
    op.loading_message("Fetching PEG Ratio")
    try:
        peg_ratio = get_peg_ratio(stock)
    except FinvizError as e:
        peg_ratio = None
        op.log_error(e)

    try:
        eps_current = get_eps_growth(stock, 0)
    except FinvizError as e:
        eps_current = None
        op.log_error(e)

    try:
        eps_1yr = get_eps_growth(stock, 1)
    except FinvizError as e:
        eps_1yr = None
        op.log_error(e)
    
    try:
        eps_5yr = get_eps_growth(stock)
    except FinvizError as e:
        eps_5yr = None
        op.log_error(e)

    company_npm, industry_npm, roe_company, roe_industry, dtoe_company, dtoe_industry = zacks_api.get_industry_comparisons(stock)

    results = {
        VIKeys.company_name.value: get_company_name(stock),
        VIKeys.symbol.value: stock,
        VIKeys.current_ratio.value: current_ratio,
        VIKeys.current_ratio_check.value: current_ratio_check,
        VIKeys.cash_flow_from_financing.value: calculate_flow_graph(
            cash_from_investments, CASH_FLOW_FROM_FINANCING_THRESHOLD),
        VIKeys.cash_flow_from_investing.value: calculate_flow_graph(
            cash_from_financing, CASH_FLOW_FROM_INVESTING_THRESHOLD),
        VIKeys.free_cash_flow.value: free_cash_flows,
        VIKeys.free_cash_flow_trend.value: fuzzy_increase(
            stret.FREE_CASH_FLOWS_ATTR, free_cash_flows),
        VIKeys.debt_to_equity_ratio.value: de_ratios,
        VIKeys.debt_to_equity_ratio_trend.value: fuzzy_increase(
            stret.DEBT_TO_EQUITY_RATIO_ATTR, de_ratios),
        VIKeys.debt_servicing_ratio_free_cash_flow.value: debt_servicing_ratios_fcf,
        VIKeys.debt_servicing_ratio_free_cash_flow_decision.value: calculate_flow_graph(
            [debt_servicing_ratios_fcf], DEBT_SERVICING_RATIO_THRESHOLD),
        VIKeys.cash_flow_from_ops.value: cash_flow_from_ops,
        VIKeys.cash_flow_from_ops_trend.value: fuzzy_increase(
            stret.CASH_FLOW_FROM_OPERATIONS_ATTR, cash_flow_from_ops),
        VIKeys.eps.value: eps_diluted,
        VIKeys.eps_trend.value: fuzzy_increase(
            stret.EPS_DILUTED_ATTR, eps_diluted),
        VIKeys.net_incomes.value: net_incomes,
        VIKeys.net_incomes_trend.value: fuzzy_increase(
            stret.NET_INCOME_ATTR, net_incomes),
        VIKeys.revenues.value: revenues,
        VIKeys.revenues_trend.value: fuzzy_increase(
            stret.REVENUE_ATTR, revenues),
        VIKeys.gross_margin.value: gross_margin,
        VIKeys.gross_margin_trend.value: fuzzy_increase(
            stret.GROSS_MARGIN_ATTR, gross_margin),
        VIKeys.net_profit_margin.value: net_profit_margins,
        VIKeys.net_profit_margin_trend.value: fuzzy_increase(
            stret.NET_PROFIT_MARGIN_ATTR, net_profit_margins),
        VIKeys.peg_ratio.value: peg_ratio,
        VIKeys.peg_ratio_check.value: evaluate_peg_ratio(peg_ratio),
        VIKeys.years.value: years,
        VIKeys.free_cash_flow_revenue.value: fcf_revenues,
        VIKeys.return_on_equity_fcf.value: return_on_equity_fcf,
        VIKeys.return_on_equity_net_income.value: return_on_equity_net_income,
        VIKeys.quarters.value: quarters,
        VIKeys.eps_current.value: eps_current,
        VIKeys.eps_1yr.value: eps_1yr,
        VIKeys.eps_5yr.value: eps_5yr,
        VIKeys.company_npm.value: company_npm,
        VIKeys.industry_npm.value: industry_npm,
        VIKeys.roe_company.value: roe_company,
        VIKeys.roe_industry.value: roe_industry,
        VIKeys.dtoe_company.value: dtoe_company,
        VIKeys.dtoe_industry.value: dtoe_industry
    }
    op.print_value_investing_report(results, VIKeys)
