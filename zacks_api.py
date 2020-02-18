from requests_html import HTMLSession
from decorators import retryable
from bs4 import BeautifulSoup

@retryable
def get_industry_comparisons(stock):
    url = f"https://www.zacks.com/stock/research/{stock}/industry-comparison"
    sess = HTMLSession()
    s = sess.get(url)
    s.html.render()
    soup = BeautifulSoup(s.html.html, "lxml")
    rows = soup.find_all('td')
    for i in range(len(rows)):
        current = rows[i].string
        if current != None:
            current_stripped = current.strip()
            if current_stripped == "Net Profit Margin (TTM)":
                company_npm = rows[i+1].string.strip()
                industry_npm = rows[i+2].string.strip()
            elif current_stripped == "Return on Equity (TTM)":
                roe_company = rows[i+1].string.strip()
                roe_industry = rows[i+2].string.strip()
            elif current_stripped == "Debt to Equity (MRQ)":
                dtoe_company = rows[i+1].string.strip()
                dtoe_industry = rows[i+2].string.strip()
    return (company_npm, industry_npm, roe_company, roe_industry, dtoe_company, dtoe_industry)

