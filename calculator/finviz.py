#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Custom Finviz.com API that grabs stock information
"""

import requests
from bs4 import BeautifulSoup

from calculator.exceptions import FinvizError


def _get_finviz_stock_page(stock_symbol: str) -> BeautifulSoup:
    page = requests.get(f"https://finviz.com/quote.ashx?t={stock_symbol}")
    return BeautifulSoup(page.content, 'html.parser')


def _get_finviz_stock_table(stock_symbol: str) -> [str]:
    page = _get_finviz_stock_page(stock_symbol)
    return page.find_all('td', class_="snapshot-td2")


def get_eps_growth(stock_symbol: str, time_frame=5) -> float:
    if time_frame == 0:
        index = 20
    elif time_frame == 1:
        index = 26
    else:
        index = 32
    stock_table = _get_finviz_stock_table(stock_symbol)
    eps_growth = stock_table[index].get_text()
    try:
        return float(eps_growth[:-1])
    except ValueError:
        raise FinvizError("Finviz - EPS not found")


def get_no_shares(stock_symbol: str) -> float:
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
        raise FinvizError("Finviz - No. shares not found")


def get_beta(stock_symbol: str) -> float:
    stock_table = _get_finviz_stock_table(stock_symbol)
    beta = stock_table[41].get_text()
    try:
        return float(beta)
    except ValueError:
        raise FinvizError("Finviz - Beta value not found")


def get_peg_ratio(stock_symbol: str) -> float:
    stock_table = _get_finviz_stock_table(stock_symbol)
    try:
        peg_ratio = stock_table[13].get_text()
        return float(peg_ratio)
    except (ValueError, IndexError):
        raise FinvizError("Finviz - PEG ratio not found")


def get_company_name(stock_symbol: str) -> str:
    page = _get_finviz_stock_page(stock_symbol)
    page_elements = page.find_all('a', class_="tab-link")
    return page_elements[12].get_text()
