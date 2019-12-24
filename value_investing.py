import urllib.request
import output as op
import operator
import json

def calculate_current_ratio(balance_sheet):
    financial_statements = balance_sheet['financials']
    float_val_liabilities = float(
        financial_statements[0]['Total current liabilities'])
    float_val_assets = float(
        financial_statements[0]['Total current assets'])
    return float_val_assets/float_val_liabilities

def calculate_debt_to_equity_ratio(balance_sheet):
    financial_statements = balance_sheet['financials']
    de_ratios = []
    for i in range(len(balance_sheet)):
        float_val_liabilities = float(
            financial_statements[i]['Total liabilities'])
        float_val_equity = float(
            financial_statements[i]['Total shareholders equity'])
    return float_val_liabilities/float_val_equity

def cash_flow(cash_flow_statements):
    financial_statements = cash_flow_statements['financials']
    cash_flow_from_operations = []
    for i in range(len(financial_statements)):
        try:
            float_cash_flow_from_ops = float(
                financial_statements[i]['Operating Cash Flow'])
            cash_flow_from_operations.append(float_cash_flow_from_ops)
        except ValueError:
            print("ERROR CASH FLOW")
    return fuzzy_increase(CASH_FLOW_FROM_OPERATIONS_ATTR, cash_flow_from_operations)

def eps(cash_flow_statements):
    pass

def score_statement_attribute(statement, statement_attribute):
    float_vals = []
    financial_statements = statement['financials']
    try:
        for i in range(len(financial_statements)):
            float_val = float(financial_statements[i][statement_attribute.attribute_name])
            float_vals.append(float_val)
    except ValueError:
        print("ERROR " + financial_statements[i][statement_attribute.attribute_name])
    return fuzzy_increase(statement_attribute, float_vals)


def multi_stock_value_score(statements):
    results = []
    for statement in statements['financialStatementList']:
        results.append(screen_income_statement(statement))
    return results

def screen_income_statement(statement):
    results = {
        REVENUE_ATTR: op.clean_boolean(score_statement_attribute(statement, REVENUE_ATTR)),
        GROSS_PROFIT_ATTR: op.clean_boolean(score_statement_attribute(
            statement, GROSS_PROFIT_ATTR)),
        GROSS_MARGIN_ATTR: op.clean_boolean(score_statement_attribute(
            statement, GROSS_MARGIN_ATTR)),
        NET_PROFIT_MARGIN_ATTR: op.clean_boolean(score_statement_attribute(
            statement, NET_PROFIT_MARGIN_ATTR)),
        EPS_DILUTED_ATTR: op.clean_boolean(score_statement_attribute(
            statement, EPS_DILUTED_ATTR))
    }
    return results



def main(stock_list):
    if len(stock_list) == 0: return
    stocks = ','.join(symbol.upper() for symbol in stock_list)
    income_statements = _get_financial_statement(INCOME_STATEMENT, stocks)
    balance_sheets = _get_financial_statement(BALANCE_SHEET, stocks, quarterly=True)
    cash_flow_statements = _get_financial_statement(
        CASH_FLOW_STATEMENT, stocks)
    if len(stock_list) > 1:
        print(multi_stock_value_score(income_statements))
    else:
        print(screen_income_statement(income_statements))

if __name__ == "__main__":
    main(["AAPL"])

# income statement
# TODO gross profit higher than industry
# TODO net profit higher than industry
