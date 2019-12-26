import statement_retrieval as stret
from fuzzy import fuzzy_increase
import urllib.request
import output as op
import operator
import json

def calculate_current_ratio(balance_sheet):
    financial_statements = balance_sheet[stret.StatementKeys.financials.value]
    float_val_liabilities = float(
        financial_statements[0][stret.StatementKeys.total_current_liabilities.value])
    float_val_assets = float(
        financial_statements[0][stret.StatementKeys.total_current_assets.value])
    return float_val_assets/float_val_liabilities

def calculate_debt_to_equity_ratio(balance_sheet):
    financial_statements = balance_sheet[stret.StatementKeys.financials.value]
    de_ratios = []
    for i in range(len(balance_sheet)):
        float_val_liabilities = float(
            financial_statements[i][stret.StatementKeys.total_liabilities.value])
        float_val_equity = float(
            financial_statements[i][stret.StatementKeys.total_shareholder_equity])
    return float_val_liabilities/float_val_equity

def is_cash_flow_increasing(cash_flow_statements):
    financial_statements = cash_flow_statements[stret.StatementKeys.financials.value]
    cash_flow_from_operations = []
    for i in range(len(financial_statements)):
        try:
            float_cash_flow_from_ops = float(
                financial_statements[i][stret.StatementKeys.operating_cash_flow.value])
            cash_flow_from_operations.append(float_cash_flow_from_ops)
        except ValueError:
            print("ERROR CASH FLOW")
    return fuzzy_increase(stret.CASH_FLOW_FROM_OPERATIONS_ATTR, cash_flow_from_operations)

def is_eps_increasing(cash_flow_statements):
    pass

def score_statement_attribute(statement, statement_attribute):
    float_vals = []
    financial_statements = statement[stret.StatementKeys.financials.value]
    try:
        for i in range(len(financial_statements)):
            float_val = float(financial_statements[i][statement_attribute.attribute_name])
            float_vals.append(float_val)
    except ValueError:
        print("ERROR " + financial_statements[i][statement_attribute.attribute_name])
    return fuzzy_increase(statement_attribute, float_vals)


def multi_stock_value_score(statements):
    results = []
    for statement in statements[stret.StatementKeys.financial_statements_list.value]:
        results.append(screen_income_statement(statement))
    return results

def screen_income_statement(statement):
    results = {
        stret.REVENUE_ATTR: op.clean_boolean(score_statement_attribute(statement, stret.REVENUE_ATTR)),
        stret.GROSS_PROFIT_ATTR: op.clean_boolean(score_statement_attribute(
            statement, stret.GROSS_PROFIT_ATTR)),
        stret.GROSS_MARGIN_ATTR: op.clean_boolean(score_statement_attribute(
            statement, stret.GROSS_MARGIN_ATTR)),
        stret.NET_PROFIT_MARGIN_ATTR: op.clean_boolean(score_statement_attribute(
            statement, stret.NET_PROFIT_MARGIN_ATTR)),
        stret.EPS_DILUTED_ATTR: op.clean_boolean(score_statement_attribute(
            statement, stret.EPS_DILUTED_ATTR))
    }
    return results



def main(stock_list):
    if len(stock_list) == 0: return
    stocks = ','.join(symbol.upper() for symbol in stock_list)
    income_statements = stret.get_financial_statement(
        stret.INCOME_STATEMENT, stocks)
    balance_sheets = stret.get_financial_statement(
        stret.BALANCE_SHEET, stocks, quarterly=True)
    cash_flow_statements = stret.get_financial_statement(
        stret.CASH_FLOW_STATEMENT, stocks)
    if len(stock_list) > 1:
        print(multi_stock_value_score(income_statements))
    else:
        print(screen_income_statement(income_statements))

if __name__ == "__main__":
    main(["AAPL"])

# income statement
# TODO gross profit higher than industry
# TODO net profit higher than industry
