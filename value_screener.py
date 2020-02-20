import time
from urllib.error import HTTPError

from tqdm import tqdm

import intrinsic_value_calculator as ivc
import output as op
from exceptions import FinvizError, DocumentError
from finviz import get_peg_ratio
from stock_list import get_all_stocks, StockListKeys

MAX_NETWORK_RETRIES: int = 5
IVC_BUFFER_VALUE: int = 500
DELAY_TIME: int = 10


def main(start_index=0) -> None:
    op.print_title_panel("Value Screener Pro")
    all_stocks = get_all_stocks()
    for stock in tqdm(all_stocks[start_index:]):
        symbol = stock[StockListKeys.symbol.value]
        tqdm.write(symbol)
        num_retries = 0
        try:
            if get_peg_ratio(symbol) <= 1.7:
                results = ivc.main(symbol, show=False)
                if ((results[ivc.IVCKeys.evaluation.value][
                         ivc.IVCKeys.market_delta_cash_flow.value] < IVC_BUFFER_VALUE or
                     results[ivc.IVCKeys.evaluation.value][
                         ivc.IVCKeys.market_delta_net_income.value] < IVC_BUFFER_VALUE) or (
                        results[ivc.IVCKeys.evaluation.value][
                            ivc.IVCKeys.market_delta_cash_flow.value] > IVC_BUFFER_VALUE or
                        results[ivc.IVCKeys.evaluation.value][
                            ivc.IVCKeys.market_delta_net_income.value] > IVC_BUFFER_VALUE)):
                    op.print_intrinsic_value(results, ivc.IVCKeys)
        except (FinvizError, DocumentError, TypeError) as e:
            op.log_error(e)
        except HTTPError as h:
            if num_retries == MAX_NETWORK_RETRIES:
                op.log_verbose("Network Congestion")
            else:
                num_retries += 1
                time.sleep(DELAY_TIME)
