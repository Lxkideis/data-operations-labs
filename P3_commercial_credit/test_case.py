import unittest
from run import evaluate
class CreditTests(unittest.TestCase):
    def test_interest_and_working_capital_units(self):
        r=evaluate(365000,.2,100000,20000,.1,60,50,40)
        self.assertEqual(r['interest_sgd'],10000)
        self.assertEqual(r['cash_conversion_cycle_days'],70)
        self.assertEqual(r['operating_working_capital_sgd'],66500)
        self.assertAlmostEqual(r['ebit_interest_coverage'],6.3875,places=3)
if __name__=='__main__':unittest.main()
