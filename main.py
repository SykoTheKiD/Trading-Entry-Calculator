from dotenv import load_dotenv

import swing
import value

def main():
    trading_methods = {1: swing.main, 2: value.main}
    while True:
        trade_type = input("What type of trading will you be doing\n1.Swing Trading\n2.Value Investing")
        stocks = input("Enter each stock symbol separated by a space ")
        stock_list = stocks.split(" ")
        if trade_type in trading_methods:
            trading_methods[trade_type](stock_list)
        else:
            exit()

if __name__ == "__main__":
    load_dotenv()
    main()
