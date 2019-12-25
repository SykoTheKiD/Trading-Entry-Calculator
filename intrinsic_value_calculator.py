import statement_retrieval as stret
from pprint import pprint
import output as op

NUM_YEARS_PROJECTED = 10


def get_discount_from_beta(discount_rate):
    rate = round(discount_rate, 1)
    if rate <= 0.8:
        return 0.05
    elif rate<= 1:
        return 0.06
    elif rate <= 1.1:
        return 0.065
    elif rate <= 1.2:
        return 0.07
    elif rate <= 1.3:
        return 0.075
    elif rate <= 1.4:
        return 0.08
    elif rate <= 1.5:
        return 0.085
    else:
        return 0.09

def get_cash_flows(cash_flow_statements):
    statements = cash_flow_statements["financials"]
    cash_flow_values = []
    for statement in statements:
        try:
            cash_flow = float(statement["Operating Cash Flow"])
            cash_flow_values.append(cash_flow)
        except ValueError:
            print(statement["Operating Cash Flow"])
    return cash_flow_values

def get_net_incomes(income_statements):
    statements = income_statements["financials"]
    cash_flow_values = []
    for statement in statements:
        try:
            cash_flow = float(statement["Net Income"])
            cash_flow_values.append(cash_flow)
        except ValueError:
            print(statement["Net Income"])
    return cash_flow_values


def get_total_debt(qrtrly_balance_sheets):
    latest_statement = qrtrly_balance_sheets["financials"][0]
    try:
        short_term_debt = float(latest_statement["Short-term debt"])
        long_term_debt = float(latest_statement["Long-term debt"])
        return short_term_debt + long_term_debt
    except ValueError:
        return -1


def get_total_cash_on_hand(qrtrly_balance_sheets):
    latest_statement = qrtrly_balance_sheets["financials"][0]
    try:
        return float(latest_statement["Cash and short-term investments"])
    except ValueError:
        return -1

def get_projected_cash_flow(current_cash, initial_growth, projected_growth):
    curr = current_cash
    projected_growths = []
    for i in range(NUM_YEARS_PROJECTED):
        if i < 5: growth = initial_growth
        else: growth = projected_growth
        next_year_cash = curr*(1 + growth)
        projected_growths.append(next_year_cash)
        curr = next_year_cash
    return projected_growths

def calculate_discount_rates(inital_discount_rate):
    discount_rates = []
    for i in range(NUM_YEARS_PROJECTED):
        rate = 1/(1 + inital_discount_rate)**(i+1)
        discount_rates.append(rate)
        cur_rate = rate
    return discount_rates

def calculate_discounted_values(projected_cash_flows, discount_rates):
    assert len(projected_cash_flows) == len(discount_rates)
    discounted_values = []
    for i in range(len(discount_rates)):
        discounted_values.append(projected_cash_flows[i] * discount_rates[i])
    return discounted_values


def calculate_intrinsic_value(projected_growth_sum, no_outstanding_shares, total_debt, total_cash_and_short_term_investments):
    intrinsic_value_prior = projected_growth_sum / no_outstanding_shares
    debt_per_share = total_debt / no_outstanding_shares
    cash_per_share = total_cash_and_short_term_investments/ no_outstanding_shares
    intrinsic_value = intrinsic_value_prior - debt_per_share + cash_per_share
    return {"Intrinsic Value Prior": intrinsic_value_prior,
            "Debt Per Share": debt_per_share,
            "Cash Per Share": cash_per_share,
            "Intrinsic Value": intrinsic_value}

def main():
    # INPUT
    stock = "AAPL"

    income_statements_yrly = stret.get_financial_statement(stret.INCOME_STATEMENT, stock)
    cash_flow_statements_yrly = stret.get_financial_statement(
        stret.CASH_FLOW_STATEMENT, stock)

    # cash flow from ops
    # use net income if cash flow from ops not increasing
    # if net income not increasing as well skip

    cash_flow_from_ops = get_cash_flows(cash_flow_statements_yrly)
    net_incomes = get_net_incomes(income_statements_yrly)

    # total debt (short term + long) latest quarter
    balance_sheets_qrtrly = stret.get_financial_statement(stret.BALANCE_SHEET,stock, quarterly=True)
    total_debt = get_total_debt(balance_sheets_qrtrly)
    if total_debt == -1:
        exit
    # cash and short term investments
    total_cash_and_short_term_investments = get_total_cash_on_hand(
        balance_sheets_qrtrly)
    if total_cash_and_short_term_investments == -1:
        exit

    # INPUT
    projected_growth_5Y = 9.86
    projected_growth = projected_growth_5Y / 2

    projected_growth_5Y = projected_growth_5Y / 100
    projected_growth = projected_growth / 100
    
    current_year_cash_flow = cash_flow_from_ops[0]
    current_year_net_income = net_incomes[0]

    projected_growths_cash_flow = get_projected_cash_flow(current_year_cash_flow, projected_growth_5Y, projected_growth)
    projected_growths_net_income = get_projected_cash_flow(
        current_year_net_income, projected_growth_5Y, projected_growth)

    # INPUT
    no_outstanding_shares = 4.45 * 1e9
    beta_value = 1.23

    discounted_rates = calculate_discount_rates(
        get_discount_from_beta(beta_value))

    intrisic_value_cash_flow = calculate_intrinsic_value(sum(
        projected_growths_cash_flow), no_outstanding_shares, total_debt, total_cash_and_short_term_investments)
    
    projected_cash_flow_discounted = calculate_discounted_values(projected_growths_cash_flow, discounted_rates)
    
    intrisic_value_net_income = calculate_intrinsic_value(sum(
        projected_growths_net_income), no_outstanding_shares, total_debt, total_cash_and_short_term_investments)
    
    projected_net_income_discounted = calculate_discounted_values(
        projected_growths_net_income, discounted_rates)
    
    results = {
        "Symbol": stock,
        "Total Debt": total_debt,
        "Total Cash on Hand": total_cash_and_short_term_investments,
        "EPS 5Y": projected_growth_5Y,
        "Projected Growth": projected_growth,
        "No. of Shares Outstanding": no_outstanding_shares,
        "Cash Flow From Ops Calculations":{
            "Cash Flow from Ops": current_year_cash_flow,
            "Present Value of 10 yr Cash Flows (Cash flow from Ops)": projected_growths_cash_flow,
            "Discount Rates": discounted_rates,
            "Projected Growth (Discounted)": projected_cash_flow_discounted,
            "Intrinsic Value": intrisic_value_cash_flow

        },
        "Net Income Calculations":{
            "Net Income": current_year_net_income,
            "Present Value of 10 yr Cash Flows (Net Income)": projected_growths_net_income,
            "Discount Rates": discounted_rates,
            "Projected Growth (Discounted)": projected_net_income_discounted,
            "Intrinsic Value": intrisic_value_net_income
        }
    }
    op.display_intrinsic_value(results)

if __name__ == "__main__":
    main()
