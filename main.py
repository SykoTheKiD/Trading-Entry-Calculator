import intrinsic_value_calculator
from dotenv import load_dotenv
import value_investing
import value_screener
import swing

TITLE_LENGTH = 45

def main():
    try:
        while True:
            print("=" * TITLE_LENGTH)
            print("\tWelcome to Trading Pro 2020")
            print("=" * TITLE_LENGTH)
            trade_type = input("What type of trading will you be doing\n\t1.Swing Trading\n\t2.Value Investing\n\t3.Screen For Value Stocks\n\t4.View Glossary --> ")
            if trade_type == "1" or trade_type == "2":
                stocks = input("Enter each stock symbol separated by a space:\n")
                stock_list = stocks.split(" ")
                if trade_type == "1":
                    swing.main(stock_list)
                elif trade_type == "2":
                    for i in stock_list:
                        value_investing.main(i)
                        intrinsic_value_calculator.main(i)
            elif trade_type == "3":
                value_screener.main()
            else:
                exit()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        exit()

if __name__ == "__main__":
    load_dotenv()
    main()
