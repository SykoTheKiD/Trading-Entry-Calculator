from bs4 import BeautifulSoup
from requests_html import HTMLSession

from decorators import retryable

MAX_RETRIES: int = 3


@retryable(MAX_RETRIES)
def get_table_rows_from_url(url: str) -> list:
    sess = HTMLSession()
    s = sess.get(url)
    s.html.render()
    soup = BeautifulSoup(s.html.html, "lxml")
    rows = soup.find_all('td')
    return rows


def get_industry_comparisons(stock: str) -> (str, str, str, str, str, str):
    company_npm = None
    industry_npm = None
    roe_company = None
    roe_industry = None
    debt_to_equity_company = None
    debt_to_equity_industry = None
    url = f"https://www.zacks.com/stock/research/{stock}/industry-comparison"
    rows = get_table_rows_from_url(url)
    for i in range(len(rows)):
        current = rows[i].string
        if current is not None:
            current_stripped = current.strip()
            if current_stripped == "Net Profit Margin (TTM)":
                company_npm = rows[i + 1].string.strip()
                industry_npm = rows[i + 2].string.strip()
            elif current_stripped == "Return on Equity (TTM)":
                roe_company = rows[i + 1].string.strip()
                roe_industry = rows[i + 2].string.strip()
            elif current_stripped == "Debt to Equity (MRQ)":
                debt_to_equity_company = rows[i + 1].string.strip()
                debt_to_equity_industry = rows[i + 2].string.strip()
    return company_npm, industry_npm, roe_company, roe_industry, debt_to_equity_company, debt_to_equity_industry


def get_company_debts(stock_symbol: str) -> (float, float):
    url = f"https://www.barchart.com/stocks/quotes/{stock_symbol}/balance-sheet/quarterly"
    rows = get_table_rows_from_url(url)
    short_term_debt = 0
    long_term_debt = 0
    for i in range(len(rows)):
        if rows[i].string is not None:
            if rows[i].string.strip() == "Short Term Debt":
                short_term_debt = float(rows[i + 1].string.strip()
                                        .replace(',', ''))
            if rows[i].string.strip() == "Long Term Debt $M":
                long_term_debt = float(rows[i + 1].string.strip()
                                       .replace(',', ''))
    return short_term_debt, long_term_debt
