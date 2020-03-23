import os
import time

import intrinsic_value_calculator
import output as op
import swing
import value_investing
import value_screener


def get_value_report(stock_list) -> None:
    for i in stock_list:
        value_investing.main(i)
        intrinsic_value_calculator.main(i)
        time.sleep(3)


def main() -> None:
    try:
        while True:
            op.print_title_panel("Welcome to TradingPro 2020")
            trade_type = input("What type of trading will you be doing\n\t1.Swing Trading\n\t2.Value "
                               "Investing\n\t3.Screen For Value Stocks\n\t4.Portfolio Evaluator --> ")
            if trade_type == "1" or trade_type == "2":
                stocks = input("Enter each stock symbol separated by a space:\n")
                stock_list = stocks.split(" ")
                if trade_type == "1":
                    swing.main(stock_list)
                elif trade_type == "2":
                    get_value_report(stock_list)
            elif trade_type == "3":
                start_index = input("Enter a start index to begin searching --> ")
                try:
                    if start_index == "":
                        start_index = 0
                    start_index = int(start_index)
                    value_screener.main(start_index)
                except ValueError:
                    value_screener.main()
            elif trade_type == "4":
                portfolio = input("\nEnter name of portfolio --> ")
                try:
                    with open(os.path.join(os.getcwd(), "portfolios", f"{portfolio}.txt")) as f:
                        lines = f.readlines()
                        lines = [p.strip() for p in lines]
                    get_value_report(lines)
                except FileNotFoundError:
                    print("Portfolio file not found")
            else:
                exit()
    except (KeyboardInterrupt, EOFError):
        print("\n\nGoodbye!")
        exit()


if __name__ == "__main__":
    main()
