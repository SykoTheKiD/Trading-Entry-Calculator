from enum import Enum
import urllib.request
import json
import ssl
import os

API_KEY = os.getenv('SWING_API_KEY')

class PricePayloadKeys(Enum):
    symbol = "symbol"
    open_price = "open"
    high = "high"
    low = "low"
    price = "price"
    volume = "volume"
    last_trading_day = "last trading day"
    previous_close = "previous close"
    change = "change"
    change_percent = "change_percent"


def get_last_price_data(stock_symbol):
    #SSL bypass hardcoded, it's fine because it's a simple API call with no personal details
    with urllib.request.urlopen(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock_symbol}&apikey={API_KEY}", context=ssl.SSLContext()) as url:
        data = json.loads(url.read().decode())
    try:
        data = data["Global Quote"]
        payload = {
            "symbol": data["01. symbol"],
            "open": data["02. open"],
            "high": data["03. high"],
            "low": data["04. low"],
            "price": data["05. price"],
            "volume": data["06. volume"],
            "last trading day": data["07. latest trading day"],
            "previous close": data["08. previous close"],
            "change": data["09. change"],
            "change percent": data["10. change percent"]
        }
        return payload
    except KeyError:
        raise KeyError("JSON Response Corrupt")

