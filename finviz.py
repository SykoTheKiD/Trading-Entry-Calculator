#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' Custom Finviz.com API that grabs stock information
'''

from exceptions import FinvizError
from bs4 import BeautifulSoup
import requests

def _get_finviz_stock_page(stock_symbol):
    page = requests.get(f"https://finviz.com/quote.ashx?t={stock_symbol}")
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def _get_finviz_stock_table(stock_symbol):
    page = _get_finviz_stock_page(stock_symbol)
    page_elements = page.find_all('td', class_="snapshot-td2")
    return page_elements

def get_eps_growth_5Y(stock_symbol):
    stock_table = _get_finviz_stock_table(stock_symbol)
    eps_5Y = stock_table[32].get_text()
    try:
        return float(eps_5Y[:-1])
    except ValueError:
        raise FinvizError

def get_no_shares(stock_symbol):
    stock_table = _get_finviz_stock_table(stock_symbol)
    try:
        no_shares = stock_table[4].get_text()
        scale = no_shares[len(no_shares) - 1]
        if scale == "B":
            factor = 1e9
        elif scale == "M":
            factor = 1e6
        else:
            factor = 1e3
        no_shares_float = float(no_shares[:-1]) * factor
        return no_shares_float
    except ValueError:
        raise FinvizError

def get_beta(stock_symbol):
    stock_table = _get_finviz_stock_table(stock_symbol)
    beta = stock_table[41].get_text()
    try:
        return float(beta)
    except ValueError:
        raise FinvizError

def get_peg_ratio(stock_symbol):
    stock_table = _get_finviz_stock_table(stock_symbol)
    try:
        peg_ratio = stock_table[13].get_text()
        return float(peg_ratio)
    except (ValueError, IndexError):
        raise FinvizError

def get_company_name(stock_symbol):
    page = _get_finviz_stock_page(stock_symbol)
    page_elements = page.find_all('a', class_="tab-link")
    return page_elements[12].get_text()
