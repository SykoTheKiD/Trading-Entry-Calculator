import urllib.request
import operator
import json
import ssl


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

REVENUE_ATTR = StatementAttribute('Revenue', BALANCE_SHEET, operator.ge)
GROSS_PROFIT_ATTR = StatementAttribute(
    'Gross Profit', INCOME_STATEMENT, operator.ge)
NET_INCOME_ATTR = StatementAttribute(
    'Net Income', INCOME_STATEMENT, operator.gt)
GROSS_MARGIN_ATTR = StatementAttribute(
    'Gross Margin', INCOME_STATEMENT, operator.ge)
NET_PROFIT_MARGIN_ATTR = StatementAttribute(
    'Net Profit Margin', INCOME_STATEMENT, operator.ge)
EPS_DILUTED_ATTR = StatementAttribute(
    'EPS Diluted', INCOME_STATEMENT, operator.gt)
CASH_FLOW_FROM_OPERATIONS_ATTR = StatementAttribute(
    'Operating Cash Flow', CASH_FLOW_STATEMENT, operator.ge)

def get_financial_statement(statement_type, stocks, quarterly=False):
    query_url = f"https://financialmodelingprep.com/api/v3/financials/{statement_type}/{stocks}"
    if quarterly:
        query_url += "?period=quarter"
    with urllib.request.urlopen(query_url, context=ssl.SSLContext()) as url:
        data = json.loads(url.read().decode())
    return data
