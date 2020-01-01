import urllib.request
from enum import Enum
import json
import ssl

class StockListKeys(Enum):
    symbol_list = "symbolsList"
    symbol = "symbol"

def get_all_stocks():
    query_url = "https://financialmodelingprep.com/api/v3/company/stock/list"
    with urllib.request.urlopen(query_url, context=ssl.SSLContext()) as url:
        data = json.loads(url.read().decode())
    return data[StockListKeys.symbol_list.value]
