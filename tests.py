import intrinsic_value_calculator as ivc
import unittest

class TestIntrinsicValueCalculator(unittest.TestCase):
    def setUp(self):
        self.stock = "FB"
        self.operational_cash_flow = 27956 * 1e6
        self.total_debt = 0
        self.cash_on_hand = 42309*1e6
        self.growth_rate_5Y = 22.2 / 100
        self.growth_rate_after_5Y = 22.2 / 100
        self.beta = 0.5
        self.no_shares = 2894.6 * 1e6

    def test_projected_growth(self):
        actual_projected_growths = [34162.23, 41746.25,	51013.91, 62339.00,76178.26, 93089.84, 113755.78, 139009.56, 169869.69, 207580.76]
        projected_growth = ivc.get_projected_cash_flow(
            self.operational_cash_flow, self.growth_rate_5Y, self.growth_rate_after_5Y)
        for i in range(len(actual_projected_growths)):
            p = projected_growth[i]
            q = actual_projected_growths[i] * 1e6
            self.assertTrue(abs(round(p, 2)-q) <= 4500)
    
    def test_discount_rate_from_beta(self):
        actual_discount_rate = 0.05
        discount_rate = ivc.get_discount_from_beta(self.beta)
        self.assertEqual(discount_rate, actual_discount_rate)

    def test_discounted_rates(self):
        actual_discount_rates = [0.95, 0.91, 0.86, 0.82, 0.78, 0.75, 0.71, 0.68, 0.64, 0.61]
        discounted_rates = ivc.calculate_discount_rates(
            ivc.get_discount_from_beta(self.beta))
        for i in range(len(actual_discount_rates)):
            p = actual_discount_rates[i]
            q = discounted_rates[i]
            self.assertTrue(abs(round(p, 2)-q) <= 0.01)
    
    def test_discounted_cash(self):
        actual_discounted_values = [32535.46, 37865.08, 44067.74, 51286.45, 59687.66, 69465.07, 80844.11, 94087.14, 109499.51, 127436.58]
        projected_growth = ivc.get_projected_cash_flow(
            self.operational_cash_flow, self.growth_rate_5Y, self.growth_rate_after_5Y)
        discount_rate = ivc.get_discount_from_beta(self.beta)
        discounted_rates = ivc.calculate_discount_rates(ivc.get_discount_from_beta(self.beta))
        discounted_cash_flows = ivc.calculate_discounted_values(
            projected_growth, discounted_rates)

        for i in range(len(actual_discounted_values)):
            p = discounted_cash_flows[i]
            q = actual_discounted_values[i] * 1e6
            self.assertTrue(abs(round(p, 2)-q) <= 4500)
    
    def test_intrinsic_value_calculation(self):
        actual_intrinsic_value = 258.79
        projected_growth = ivc.get_projected_cash_flow(
            self.operational_cash_flow, self.growth_rate_5Y, self.growth_rate_after_5Y)
        discount_rate = ivc.get_discount_from_beta(self.beta)
        discounted_rates = ivc.calculate_discount_rates(
            ivc.get_discount_from_beta(self.beta))
        discounted_cash_flows = ivc.calculate_discounted_values(
            projected_growth, discounted_rates)

        intrinsic_value = ivc.calculate_intrinsic_value(sum(discounted_cash_flows), self.no_shares, self.total_debt, self.cash_on_hand)

        p = intrinsic_value["Intrinsic Value"]
        q = actual_intrinsic_value
        self.assertTrue(abs(round(p, 2)-q) <= 2)

if __name__ == "__main__":
    unittest.main()
