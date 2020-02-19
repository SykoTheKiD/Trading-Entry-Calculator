import intrinsic_value_calculator
import value_investing
import value_screener
import output as op
import swing


def main():
    try:
        while True:
            op.print_title_panel("Welcome to TradingPro 2020")
            trade_type = input("What type of trading will you be doing\n\t1.Swing Trading\n\t2.Value "
                               "Investing\n\t3.Screen For Value Stocks --> ")
            if trade_type == "1" or trade_type == "2":
                stocks = input("Enter each stock symbol separated by a space:\n")
                stock_list = stocks.split(" ")
                if trade_type == "1":
                    swing.main(stock_list)
                elif trade_type == "2":
                    for i in stock_list:
                        op.print_title_panel("Value Investing Report")
                        value_investing.main(i)
                        op.print_title_panel("Intrinsic Value Report")
                        intrinsic_value_calculator.main(i)
            elif trade_type == "3":
                start_index = input("Enter a start index to begin searching --> ")
                try:
                    if start_index == "":
                        start_index = 0
                    start_index = int(start_index)
                    value_screener.main(start_index)
                except ValueError:
                    value_screener.main()
            else:
                exit()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        exit()


if __name__ == "__main__":
    main()
