import config_loader as cl

from enum import Enum
import urllib.request
import json
import ssl


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
    # SSL bypass hardcoded, it's fine because it's a simple API call with no personal details
    with urllib.request.urlopen(
            f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock_symbol}&apikey={cl.SWING_API_KEY}",
            context=ssl.SSLContext()) as url:
        data = json.loads(url.read().decode())
    try:
        data = data["Global Quote"]
        payload = {
            PricePayloadKeys.symbol.value: data["01. symbol"],
            PricePayloadKeys.open_price.value: data["02. open"],
            PricePayloadKeys.high.value: data["03. high"],
            PricePayloadKeys.low.value: data["04. low"],
            PricePayloadKeys.price.value: data["05. price"],
            PricePayloadKeys.volume.value: data["06. volume"],
            PricePayloadKeys.last_trading_day.value: data["07. latest trading day"],
            PricePayloadKeys.previous_close.value: data["08. previous close"],
            PricePayloadKeys.change.value: data["09. change"],
            PricePayloadKeys.change_percent.value: data["10. change percent"]
        }
        return payload
    except KeyError:
        raise KeyError("JSON Response Corrupt")
