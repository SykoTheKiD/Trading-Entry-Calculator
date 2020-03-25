import os
import time

import intrinsic_value_calculator
import output as op
import swing
import value_investing
import value_screener

from urllib.error import HTTPError

DEFAULT_MENU_OPTION = "2"


def get_value_report(stock_list) -> None:
    for i in stock_list:
        print(f"Performing value investment calculation for {i}")
        try:
            value_investing.main(i)
        except HTTPError:
            print(f"Stock: {i} not found")
            continue
        print(f"Performing intrinsic value calculation for {i}")
        intrinsic_value_calculator.main(i)
        time.sleep(3)


def main() -> None:
    table = [["Option", "Type"], ["1", "Swing Trading"], ["2", "Value Investing"], ["3", "Screen for Value Stock"], ["4", "Portfolio Evaluator"]]
    try:
        while True:
            op.print_title_panel("Welcome to TradingPro 2020")
            op.print_table(table)
            trade_type = input("What type of trading will you be doing\n\t--> ")
            if trade_type == "":
                trade_type = DEFAULT_MENU_OPTION
            if trade_type == "1" or trade_type == "2":
                stocks = input("Enter each stock symbol separated by a space:\n")
                stock_list = stocks.split(" ")
                if trade_type == "1":
                    print(f"Performing swing trade calculations for {stocks}")
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
                    print(f"Performing portfolio analysis for {portfolio} portfolio")
                    get_value_report(lines)
                except FileNotFoundError:
                    print("Portfolio file not found")
            else:
                exit()
    except (KeyboardInterrupt, EOFError, ConnectionResetError):
        print("\n\nGoodbye!")
        exit()


if __name__ == "__main__":
    main()
