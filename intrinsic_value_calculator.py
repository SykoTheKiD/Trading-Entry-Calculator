# TODO Format file
from enum import Enum

import finviz
import output as op
import statement_retrieval as stret
from exceptions import DocumentError
from exceptions import FinvizError
from externals import get_company_debts
from fuzzy import fuzzy_increase
from pricing import get_last_price_data, PricePayloadKeys

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
    market_delta_cash_flow = "Delta (Cash Flow)"
    market_delta_net_income = "Delta (Net Income)"
    debt_per_share = "Debt Per Share"
    intrinsic_value_prior = "Intrinsic Value Prior"
    cash_per_share = "Cash Per Share"


def get_discount_from_beta(discount_rate: float) -> float:
    rate = round(discount_rate, 1)
    if rate <= 0.8:
        return 0.05
    elif rate <= 1:
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


def get_cash_flows(cash_flow_statements: dict) -> list:
    try:
        statements = cash_flow_statements[stret.StatementKeys.financials.value]
    except KeyError as e:
        raise DocumentError
    cash_flow_values = []
    for statement in statements:
        try:
            cash_flow = float(statement[stret.StatementKeys.operating_cash_flow.value])
            cash_flow_values.append(cash_flow)
            return cash_flow_values
        except ValueError as e:
            raise e


def get_net_incomes(income_statements: dict) -> list:
    try:
        statements = income_statements[stret.StatementKeys.financials.value]
    except KeyError as e:
        raise DocumentError
    net_income_values = []
    for statement in statements:
        try:
            net_incomes = float(statement[stret.StatementKeys.net_income.value])
            net_income_values.append(net_incomes)
            return net_income_values
        except ValueError as e:
            raise e


def get_total_debt(qrtrly_balance_sheets: dict) -> float:
    try:
        stock_symbol = qrtrly_balance_sheets[stret.StatementKeys.symbol.value]
        latest_statement = qrtrly_balance_sheets[stret.StatementKeys.financials.value][0]
    except KeyError as e:
        raise DocumentError
    short_term_debt, long_term_debt = get_company_debts(stock_symbol)
    return short_term_debt + long_term_debt


def get_total_cash_on_hand(qrtrly_balance_sheets: dict) -> float:
    try:
        latest_statement = qrtrly_balance_sheets[stret.StatementKeys.financials.value][0]
    except KeyError as e:
        raise DocumentError
    try:
        return float(latest_statement[stret.StatementKeys.cash_and_short_term_investments.value])
    except ValueError as e:
        raise e


def get_projected_cash_flow(current_cash: float, initial_growth: float, projected_growth: float) -> list:
    curr = current_cash
    projected_growths = []
    for i in range(NUM_YEARS_PROJECTED):
        if i < 5:
            growth = initial_growth
        else:
            growth = projected_growth
        next_year_cash = curr * (1 + growth)
        projected_growths.append(next_year_cash)
        curr = next_year_cash
    return projected_growths


def calculate_discount_rates(inital_discount_rate: float) -> list:
    discount_rates = []
    for i in range(NUM_YEARS_PROJECTED):
        rate = 1 / (1 + inital_discount_rate) ** (i + 1)
        discount_rates.append(rate)
        cur_rate = rate
    return discount_rates


def calculate_discounted_values(projected_cash_flows: list, discount_rates: list) -> list:
    assert len(projected_cash_flows) == len(discount_rates)
    discounted_values = []
    for i in range(len(discount_rates)):
        discounted_values.append(projected_cash_flows[i] * discount_rates[i])
    return discounted_values


def calculate_intrinsic_value(projected_growth_sum: float, no_outstanding_shares: float, total_debt_current_debt: float,
                              total_cash_and_short_term_investments_current: float) -> dict:
    intrinsic_value_prior = projected_growth_sum / no_outstanding_shares
    debt_per_share = total_debt_current_debt / no_outstanding_shares
    cash_per_share = total_cash_and_short_term_investments_current / no_outstanding_shares
    intrinsic_value = intrinsic_value_prior - debt_per_share + cash_per_share
    return {IVCKeys.intrinsic_value_prior.value: intrinsic_value_prior,
            IVCKeys.debt_per_share.value: debt_per_share,
            IVCKeys.cash_per_share.value: cash_per_share,
            IVCKeys.intrinsic_value.value: intrinsic_value}


def main(stock_symbol: str, show=True) -> dict:
    global cash_flow_from_ops, net_incomes, total_debt, total_cash_and_short_term_investments
    stock_symbol = stock_symbol.upper()
    op.loading_message(f"Calculating Intrinsic Value for: {stock_symbol}")
    op.loading_message("Fetching Yearly Income Statements")
    income_statements_yearly = stret.get_financial_statement(
        stret.INCOME_STATEMENT, stock_symbol)
    op.loading_message("Fetching Yearly Cash Flow Statements")
    cash_flow_statements_yearly = stret.get_financial_statement(
        stret.CASH_FLOW_STATEMENT, stock_symbol)

    # cash flow from ops
    # use net income if cash flow from ops not increasing
    # if net income not increasing as well skip
    try:
        op.loading_message("Parsing Cash Flows from Operations")
        try:
            cash_flow_from_ops = get_cash_flows(cash_flow_statements_yearly)
        except DocumentError as e:
            op.log_error(e)

        op.loading_message("Parsing Net Incomes")
        try:
            net_incomes = get_net_incomes(income_statements_yearly)
        except DocumentError as e:
            op.log_error(e)

        # total debt (short term + long) latest quarter
        op.loading_message("Fetching Quarterly Balance Sheets")
        balance_sheets_quarterly = stret.get_financial_statement(
            stret.BALANCE_SHEET, stock_symbol, quarterly=True)
        op.loading_message("Calculating Total Debt")
        total_debt = get_total_debt(balance_sheets_quarterly)
        op.loading_message("Calculating Total Cash on Hand")
        total_cash_and_short_term_investments = get_total_cash_on_hand(
            balance_sheets_quarterly)
    except ValueError as e:
        op.log_error(e)

    try:
        projected_growth_5_y = finviz.get_eps_growth(stock_symbol)
        projected_growth_after_5_y = projected_growth_5_y / 2 if projected_growth_5_y is not None else 0

        projected_growth_5_y = projected_growth_5_y / 100 if projected_growth_5_y is not None else 0
        projected_growth_after_5_y = projected_growth_after_5_y / 100

        current_year_cash_flow = cash_flow_from_ops[0]
        current_year_net_income = net_incomes[0]

        op.loading_message("Calculating Projected Cash Flows")
        projected_growths_cash_flow = get_projected_cash_flow(
            current_year_cash_flow, projected_growth_5_y, projected_growth_after_5_y)
        op.loading_message("Calculating Projected Net Incomes")
        projected_growths_net_income = get_projected_cash_flow(
            current_year_net_income, projected_growth_5_y, projected_growth_after_5_y)

        op.loading_message("Fetching Number of Outstanding Shares from Finviz")
        no_outstanding_shares = finviz.get_no_shares(stock_symbol)
        op.loading_message("Fetching Beta Value from Finviz")
        beta_value = finviz.get_beta(stock_symbol)
    except FinvizError as e:
        op.log_error(e)
        return dict()

    discounted_rates = calculate_discount_rates(
        get_discount_from_beta(beta_value))

    op.loading_message("Calculating Discounted Projected Cash Flows")
    projected_cash_flow_discounted = calculate_discounted_values(
        projected_growths_cash_flow, discounted_rates)

    op.loading_message("Calculating Intrinsic Value from Cash Flow")
    intrinsic_value_cash_flow = calculate_intrinsic_value(sum(
        projected_cash_flow_discounted), no_outstanding_shares, total_debt, total_cash_and_short_term_investments)

    op.loading_message("Calculating Discounted Projected Cash Flows")
    projected_net_income_discounted = calculate_discounted_values(
        projected_growths_net_income, discounted_rates)

    op.loading_message("Calculating Intrinsic Value from Net Income")
    intrinsic_value_net_income = calculate_intrinsic_value(sum(
        projected_net_income_discounted), no_outstanding_shares, total_debt, total_cash_and_short_term_investments)

    market_price = float(get_last_price_data(stock_symbol)[PricePayloadKeys.price.value])
    intrinsic_value_cash_flow_final = intrinsic_value_cash_flow[IVCKeys.intrinsic_value.value]
    intrinsic_value_net_income_final = intrinsic_value_net_income[IVCKeys.intrinsic_value.value]

    try:
        peg_ratio = finviz.get_peg_ratio(stock_symbol)
    except FinvizError as e:
        peg_ratio = None
        op.log_error(e)

    results = {
        IVCKeys.company_name.value: finviz.get_company_name(stock_symbol),
        IVCKeys.symbol.value: stock_symbol,
        IVCKeys.total_debt.value: total_debt,
        IVCKeys.total_cash.value: total_cash_and_short_term_investments,
        IVCKeys.eps_5Y.value: projected_growth_5_y,
        IVCKeys.projected_growth.value: projected_growth_after_5_y,
        IVCKeys.no_shares.value: no_outstanding_shares,
        IVCKeys.cash_from_ops_calcs.value: {
            IVCKeys.cash_from_ops.value: current_year_cash_flow,
            IVCKeys.discount_rates.value: discounted_rates,
            IVCKeys.pv_of_cash.value: projected_cash_flow_discounted,
            IVCKeys.intrinsic_value.value: intrinsic_value_cash_flow

        },
        IVCKeys.net_income_calcs.value: {
            IVCKeys.net_income.value: current_year_net_income,
            IVCKeys.pv_of_cash.value: projected_growths_net_income,
            IVCKeys.discount_rates.value: discounted_rates,
            IVCKeys.projected_growth_discounted.value: projected_net_income_discounted,
            IVCKeys.intrinsic_value.value: intrinsic_value_net_income
        },
        IVCKeys.evaluation.value: {
            IVCKeys.peg.value: peg_ratio,
            IVCKeys.market_price.value: market_price,
            IVCKeys.market_delta_cash_flow.value: market_price - intrinsic_value_cash_flow_final,
            IVCKeys.market_delta_net_income.value: market_price - intrinsic_value_net_income_final,
            IVCKeys.cash_from_ops.value: fuzzy_increase(stret.CASH_FLOW_FROM_OPERATIONS_ATTR,
                                                        cash_flow_from_ops[:5][::-1]),
            IVCKeys.net_income.value: fuzzy_increase(stret.NET_INCOME_ATTR, net_incomes[:5][::-1])
        }
    }

    if show:
        op.print_intrinsic_value(results, IVCKeys)

    return results
