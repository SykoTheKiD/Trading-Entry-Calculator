from pricing import get_last_price_data, PricePayloadKeys
import statement_retrieval as stret
from fuzzy import fuzzy_increase
from enum import Enum
import output as op
import finviz

NUM_YEARS_PROJECTED = 10

class IVCKeys(Enum):
    company_name = "Company"
    symbol = "Symbol"
    total_debt = "Total Debt"
    total_cash = "Total Cash on Hand"
    eps_5Y = "EPS 5Y"
    projected_growth = "Projected Growth"
    no_shares = "No. of Shares Outstanding"
    cash_from_ops_calcs = "Cash Flow From Ops Calculations"
    cash_from_ops = "Cash Flow from Ops"
    pv_of_cash = "Present Value of 10 yr"
    discount_rates = "Discount Rates"
    projected_growth_discounted = "Projected Growth (Discounted)"
    intrinsic_value = "Intrinsic Value"
    net_income_calcs = "Net Income Calculations"
    net_income = "Net Income"
    evaluation = "Evaluation"
    peg = "PEG"
    market_price = "Current Market Price"
    market_delta = "Delta"
    debt_per_share = "Debt Per Share"
    intrinsic_value_prior = "Intrinsic Value Prior"
    cash_per_share = "Cash Per Share"

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
    statements = cash_flow_statements[stret.StatementKeys.financials.value]
    cash_flow_values = []
    for statement in statements:
        try:
            cash_flow = float(statement[stret.StatementKeys.operating_cash_flow.value])
            cash_flow_values.append(cash_flow)
        except ValueError:
            print(statement[stret.StatementKeys.operating_cash_flow.value])
    return cash_flow_values

def get_net_incomes(income_statements):
    statements = income_statements[stret.StatementKeys.financials.value]
    net_income_values = []
    for statement in statements:
        try:
            net_incomes = float(statement[stret.StatementKeys.net_income.value])
            net_income_values.append(net_incomes)
        except ValueError:
            print(statement[stret.StatementKeys.net_income.value])
    return net_income_values


def get_total_debt(qrtrly_balance_sheets):
    latest_statement = qrtrly_balance_sheets[stret.StatementKeys.financials.value][0]
    try:
        short_term_debt = float(latest_statement[stret.StatementKeys.short_term_debt.value])
        long_term_debt = float(latest_statement[stret.StatementKeys.long_term_debt.value])
        return short_term_debt + long_term_debt
    except ValueError:
        return -1


def get_total_cash_on_hand(qrtrly_balance_sheets):
    latest_statement = qrtrly_balance_sheets[stret.StatementKeys.financials.value][0]
    try:
        return float(latest_statement[stret.StatementKeys.cash_and_short_term_investments.value])
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
    return {IVCKeys.intrinsic_value_prior.value: intrinsic_value_prior,
            IVCKeys.debt_per_share.value: debt_per_share,
            IVCKeys.cash_per_share.value: cash_per_share,
            IVCKeys.intrinsic_value.value: intrinsic_value}

def main(stock_symbol):
    stock_symbol = stock_symbol.upper()
    op.loading_message(f"Calculating Intrinsic Value for: {stock_symbol}")
    op.loading_message("Fetching Yearly Income Statements")
    income_statements_yrly = stret.get_financial_statement(
        stret.INCOME_STATEMENT, stock_symbol)
    op.loading_message("Fetching Yearly Cash Flow Statements")
    cash_flow_statements_yrly = stret.get_financial_statement(
        stret.CASH_FLOW_STATEMENT, stock_symbol)

    # cash flow from ops
    # use net income if cash flow from ops not increasing
    # if net income not increasing as well skip
    op.loading_message("Parsing Cash Flows from Operations")
    cash_flow_from_ops = get_cash_flows(cash_flow_statements_yrly)
    op.loading_message("Parsing Net Incomes")
    net_incomes = get_net_incomes(income_statements_yrly)

    # total debt (short term + long) latest quarter
    op.loading_message("Fetching Quarterly Balance Sheets")
    balance_sheets_qrtrly = stret.get_financial_statement(
        stret.BALANCE_SHEET, stock_symbol, quarterly=True)
    op.loading_message("Calculating Total Debt")
    total_debt = get_total_debt(balance_sheets_qrtrly)
    if total_debt == -1:
        exit
    # cash and short term investments
    op.loading_message("Calculating Total Cash on Hand")
    total_cash_and_short_term_investments = get_total_cash_on_hand(
        balance_sheets_qrtrly)
    if total_cash_and_short_term_investments == -1:
        exit

    projected_growth_5Y = finviz.get_eps_growth_5Y(stock_symbol)
    projected_growth_after_5Y = projected_growth_5Y / 2

    projected_growth_5Y = projected_growth_5Y / 100
    projected_growth_after_5Y = projected_growth_after_5Y / 100
    
    current_year_cash_flow = cash_flow_from_ops[0]
    current_year_net_income = net_incomes[0]

    op.loading_message("Calculating Projected Cash Flows")
    projected_growths_cash_flow = get_projected_cash_flow(
        current_year_cash_flow, projected_growth_5Y, projected_growth_after_5Y)
    op.loading_message("Calculating Projected Net Incomes")
    projected_growths_net_income = get_projected_cash_flow(
        current_year_net_income, projected_growth_5Y, projected_growth_after_5Y)

    op.loading_message("Fetching Number of Outstanding Shares from Finviz")
    no_outstanding_shares = finviz.get_no_shares(stock_symbol)
    op.loading_message("Fetching Beta Value from Finviz")
    beta_value = finviz.get_beta(stock_symbol)

    discounted_rates = calculate_discount_rates(
        get_discount_from_beta(beta_value))

    op.loading_message("Calculating Discounted Projected Cash Flows")
    projected_cash_flow_discounted = calculate_discounted_values(
        projected_growths_cash_flow, discounted_rates)

    op.loading_message("Calculating Intrinsic Value from Cash Flow")
    intrisic_value_cash_flow = calculate_intrinsic_value(sum(
        projected_cash_flow_discounted), no_outstanding_shares, total_debt, total_cash_and_short_term_investments)

    op.loading_message("Calculating Discounted Projected Cash Flows")
    projected_net_income_discounted = calculate_discounted_values(
        projected_growths_net_income, discounted_rates)

    op.loading_message("Calculating Intrinsic Value from Net Income")
    intrisic_value_net_income = calculate_intrinsic_value(sum(
        projected_net_income_discounted), no_outstanding_shares, total_debt, total_cash_and_short_term_investments)

    market_price = float(get_last_price_data(stock_symbol)[PricePayloadKeys.price.value])
    intrinsic_value_cash_flow_final = intrisic_value_cash_flow[IVCKeys.intrinsic_value.value]
    intrinsic_value_net_income_final = intrisic_value_net_income[IVCKeys.intrinsic_value.value]

    results = {
        IVCKeys.company_name.value: finviz.get_company_name(stock_symbol),
        IVCKeys.symbol.value: stock_symbol,
        IVCKeys.total_debt.value: total_debt,
        IVCKeys.total_cash.value: total_cash_and_short_term_investments,
        IVCKeys.eps_5Y.value: projected_growth_5Y,
        IVCKeys.projected_growth.value: projected_growth_after_5Y,
        IVCKeys.no_shares.value: no_outstanding_shares,
        IVCKeys.cash_from_ops_calcs.value: {
            IVCKeys.cash_from_ops.value: current_year_cash_flow,
            IVCKeys.pv_of_cash.value: projected_growths_cash_flow,
            IVCKeys.discount_rates.value: discounted_rates,
            IVCKeys.pv_of_cash.value: projected_cash_flow_discounted,
            IVCKeys.intrinsic_value.value: intrisic_value_cash_flow

        },
        IVCKeys.net_income_calcs.value: {
            IVCKeys.net_income.value: current_year_net_income,
            IVCKeys.pv_of_cash.value: projected_growths_net_income,
            IVCKeys.discount_rates.value: discounted_rates,
            IVCKeys.projected_growth_discounted.value: projected_net_income_discounted,
            IVCKeys.intrinsic_value.value: intrisic_value_net_income
        },
        IVCKeys.evaluation.value: {
            IVCKeys.peg.value: finviz.get_peg_ratio(stock_symbol),
            IVCKeys.market_price.value: market_price,
            IVCKeys.market_delta.value: market_price - intrinsic_value_cash_flow_final,
            IVCKeys.market_delta.value: market_price - intrinsic_value_net_income_final,
            IVCKeys.cash_from_ops.value: fuzzy_increase(stret.CASH_FLOW_FROM_OPERATIONS_ATTR, cash_flow_from_ops[:5][::-1]), IVCKeys.net_income.value: fuzzy_increase(stret.NET_INCOME_ATTR, net_incomes[:5][::-1])
        }
    }
    op.print_intrinsic_value(results, IVCKeys)

if __name__ == "__main__":
    main("AAPL")
