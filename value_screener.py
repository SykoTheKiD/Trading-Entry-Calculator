from stock_list import get_all_stocks, StockListKeys
import intrinsic_value_calculator as ivc
from tqdm import tqdm
import output as op


if __name__ == "__main__":
    all_stocks = get_all_stocks()
    error_stocks = 0
    for stock in tqdm(all_stocks):
        symbol = stock[StockListKeys.symbol.value]
        try:
            results = ivc.main(symbol, show=False)
            if (results[ivc.IVCKeys.evaluation.value][ivc.IVCKeys.market_delta_cash_flow.value] < 0 or results[ivc.IVCKeys.evaluation.value][ivc.IVCKeys.market_delta_net_income.value] < 0) and results[ivc.IVCKeys.evaluation.value][ivc.IVCKeys.peg.value] <= 1.6:
                op.print_intrinsic_value(results)
        except Exception:
            error_stocks += 1

