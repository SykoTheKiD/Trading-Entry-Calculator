import intrinsic_value_calculator as ivc

def test_intinsic_value_calculator():
    stock = "FB"
    ocf = 27956 * 1e6
    total_debt = 0
    cash_on_hand = 42309*1e6
    growth_rate_5y = 22.2 / 100
    growth_rate_10y = 22.2 / 100
    beta = 0.5
    no_shares = 2894.6 * 1e6

    projected_growth = ivc.get_projected_cash_flow(
        ocf, growth_rate_5y, growth_rate_10y)

    print(sum(projected_growth))
    print(projected_growth)

    discounted_rates = ivc.calculate_discount_rates(ivc.get_discount_from_beta(beta))
    print(ivc.get_discount_from_beta(beta))
    print(discounted_rates)

    discounted_cashflows = ivc.calculate_discounted_values(projected_growth, discounted_rates)
    print(discounted_cashflows)

    intrinsic_value = ivc.calculate_intrinsic_value(
        sum(discounted_cashflows), no_shares, total_debt, cash_on_hand)

    print(intrinsic_value)

def main():
    test_intinsic_value_calculator()

if __name__ == "__main__":
    main()
