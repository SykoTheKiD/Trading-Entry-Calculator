import urllib.request
import json
import ssl

CASH_FLOW_STATEMENT = "cash-flow-statement"
BALANCE_SHEET = "balance-sheet-statement"
INCOME_STATEMENT = "income-statement"


def _get_financial_statement(statement_type, stocks):
    with urllib.request.urlopen(f"https://financialmodelingprep.com/api/v3/financials/{statement_type}/{stocks}", context=ssl.SSLContext()) as url:
        data = json.loads(url.read().decode())
    return data

def _fuzzy_increase(sequence):
    def __check_increasing(seq):
        for i in range(len(seq)-1):
            if seq[i] > seq[i+1]:
                return False
        return True

    check = __check_increasing(sequence)
    if check: return True
    # Check if removing an item will make a strictly increasing list
    if __check_increasing(sequence[check-1:check] + sequence[check+1:]) or __check_increasing(sequence[check:check+1] + sequence[check+2:]):
        return True
    # If not return False, since more than 1 element needs to be removed
    return False

def score_statement(statement):
    score = 0  # max score 7.5, last 5 years are weighted more
    revenue_growths = []
    financial_statements = statement['financials']
    try:
        for i in range(len(financial_statements)):
            rev_float = float(financial_statements[i]['Revenue Growth'])
            if rev_float > 0:
                if i <= 5: score += 1
                else: score += 0.5
        revenue_growths.append(rev_float)
    except ValueError:
        print("ERROR " + financial_statements[i]['Revenue Growth'])
    if _fuzzy_increase(revenue_growths): score +=1
    return score


def multi_stock_value_score(statements):
    for statement in statements['financialStatementList']:
        score_statement(statement)
    return 0

def main(stock_list):
    if len(stock_list) == 0: return
    stocks = ','.join(symbol.upper() for symbol in stock_list)
    income_statements = _get_financial_statement(INCOME_STATEMENT, stocks)
    balance_sheets = _get_financial_statement(BALANCE_SHEET, stocks)
    cash_flow_statements = _get_financial_statement(
        CASH_FLOW_STATEMENT, stocks)

    if len(stock_list) > 1:
        multi_stock_value_score(income_statements)
    else:
        score_statement(income_statements)

if __name__ == "__main__":
    main(["AAPL"])

# income statement
# annual gross profit inc yoy
# net income inc yoy
# revenue relatively inc yoy
# gross margin inc/consistent yoy
# net margin inc/consis yoy
# earnings per share inc yoy diluted
# gross profit higher than industry
# net profit higher than industry
