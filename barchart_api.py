from requests_html import HTMLSession
from decorators import retryable
from bs4 import BeautifulSoup
import sys

NUM_RETRIES = 5

@retryable(NUM_RETRIES)
def get_debts(stock_symbol):
    url = f"https://www.barchart.com/stocks/quotes/{stock_symbol}/balance-sheet/quarterly"
    session = HTMLSession()
    resp = session.get(url)
    resp.html.render()
    soup = BeautifulSoup(resp.html.html, "lxml")
    rows = soup.find_all('td')
    short_term_debt = 0
    long_term_debt = 0
    for i in range(len(rows)):
        if rows[i].string != None:
            if rows[i].string.strip() == "Short Term Debt":
                short_term_debt = float(rows[i+1].string.strip()
                .replace(',', ''))
            if rows[i].string.strip() == "Long Term Debt $M":
                long_term_debt = float(rows[i+1].string.strip()
                .replace(',', ''))
    return short_term_debt, long_term_debt
