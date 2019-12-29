import intrinsic_value_calculator
from dotenv import load_dotenv
import value_investing
import swing

def main():
    while True:
        trade_type = input("What type of trading will you be doing\n\t1.Swing Trading\n\t2.Value Investing\n")
        stocks = input("Enter each stock symbol separated by a space:\n")
        stock_list = stocks.split(" ")
        if trade_type == "1":
            swing.main(stock_list)
        elif trade_type == "2":
            for i in stock_list:
                value_investing.main(i)
                intrinsic_value_calculator.main(i)
        else:
            exit()

if __name__ == "__main__":
    load_dotenv()
    main()
