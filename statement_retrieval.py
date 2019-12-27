from enum import Enum
import urllib.request
import operator
import json
import ssl

class StatementKeys(Enum):
    financials = "financials"
    total_current_liabilities = "Total current liabilities"
    total_current_assets = "Total current assets"
    total_liabilities = "Total liabilities"
    total_shareholder_equity = "Total shareholders equity"
    operating_cash_flow = "Operating Cash Flow"
    financial_statements_list = "financialStatementList"
    eps_diluted = "EPS Diluted"
    net_profit_margin = "Net Profit Margin"
    capital_expenditure = "Capital Expenditure"
    gross_profit = "Gross Profit"
    gross_margin = "Gross Margin"
    revenue = "Revenue"
    total_assets = "Total assets"
    net_income = "Net Income"
    short_term_debt = "Short-term debt"
    long_term_debt = "Long-term debt"
    cash_and_short_term_investments = "Cash and short-term investments"
    cash_from_investments = "Investing Cash flow"
    free_cash_flows = "Free Cash Flow"
    cash_from_financing = "Financing Cash Flow"
    net_interest_expense = "Interest Expense"

class StatementAttribute:
    def __init__(self, attribute_name, attribute_document, operation):
        self.attribute_name = attribute_name
        self.attribute_document = attribute_document
        self.operation = operation

    def __repr__(self):
        return self.attribute_name

    def __str__(self):
        return self.attribute_name

CASH_FLOW_STATEMENT = "cash-flow-statement"
BALANCE_SHEET = "balance-sheet-statement"
INCOME_STATEMENT = "income-statement"

REVENUE_ATTR = StatementAttribute(StatementKeys.revenue.value, BALANCE_SHEET, operator.ge)
GROSS_PROFIT_ATTR = StatementAttribute(
    StatementKeys.gross_profit.value, INCOME_STATEMENT, operator.ge)
NET_INCOME_ATTR = StatementAttribute(
    StatementKeys.net_income.value, INCOME_STATEMENT, operator.gt)
GROSS_MARGIN_ATTR = StatementAttribute(
    StatementKeys.gross_margin.value, INCOME_STATEMENT, operator.ge)
NET_PROFIT_MARGIN_ATTR = StatementAttribute(
    StatementKeys.net_profit_margin.value, INCOME_STATEMENT, operator.ge)
EPS_DILUTED_ATTR = StatementAttribute(
    StatementKeys.eps_diluted.value, INCOME_STATEMENT, operator.gt)
CASH_FLOW_FROM_OPERATIONS_ATTR = StatementAttribute(
    StatementKeys.operating_cash_flow.value, CASH_FLOW_STATEMENT, operator.gt)
CAPITAL_EXPENDITURE_ATTR = StatementAttribute(StatementKeys.capital_expenditure.value, CASH_FLOW_STATEMENT, operator.ge)
TOTAL_ASSETS_ATTR = StatementAttribute(
    StatementKeys.total_assets.value, BALANCE_SHEET, operator.ge)
TOTAL_CURRENT_ASSETS_ATTR = StatementAttribute(
    StatementKeys.total_current_assets.value, BALANCE_SHEET, operator.ge)
TOTAL_LIABILITIES_ATTR = StatementAttribute(
    StatementKeys.total_liabilities.value, BALANCE_SHEET, operator.ge)
TOTAL_CURRENT_LIABILITIES_ATTR = StatementAttribute(
    StatementKeys.total_current_liabilities.value, BALANCE_SHEET, operator.ge)
TOTAL_SHAREHOLDER_EQUITY_ATTR = StatementAttribute(
    StatementKeys.total_shareholder_equity.value, BALANCE_SHEET, operator.ge)
FREE_CASH_FLOWS_ATTR = StatementAttribute(StatementKeys.free_cash_flows.value, CASH_FLOW_STATEMENT, operator.ge)
CASH_FROM_INVESTMENTS_ATTR = StatementAttribute(StatementKeys.cash_from_investments.value, CASH_FLOW_STATEMENT, operator.ge)
CASH_FROM_FINANCING_ATTR = StatementAttribute(StatementKeys.cash_from_financing.value, CASH_FLOW_STATEMENT, operator.ge)
INTEREST_EXPENSE_ATTR = StatementAttribute(StatementKeys.net_interest_expense.value, INCOME_STATEMENT, operator.ge)
DEBT_TO_EQUITY_RATIO_ATTR = StatementAttribute(None, None, operator.le)


def get_financial_statement(statement_type, stocks, quarterly=False):
    query_url = f"https://financialmodelingprep.com/api/v3/financials/{statement_type}/{stocks}"
    if quarterly:
        query_url += "?period=quarter"
    with urllib.request.urlopen(query_url, context=ssl.SSLContext()) as url:
        data = json.loads(url.read().decode())
    return data
