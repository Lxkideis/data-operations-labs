import unittest
from run import summary,run
class SLOTests(unittest.TestCase):
    def test_fast_error_and_slow_success_both_consume_budget(self):
        r=summary([{'status':200,'latency_ms':10},{'status':503,'latency_ms':2},{'status':200,'latency_ms':50}])
        self.assertEqual(r['observed_bad_requests'],2)
        self.assertAlmostEqual(r['http_success_rate'],2/3,places=4)
        self.assertEqual(r['p95_latency_ms'],50)
    def test_actual_local_http_fault_and_recovery(self):
        r=run()['phases']
        self.assertEqual(r['baseline']['http_success_rate'],1)
        self.assertEqual(r['injected']['http_success_rate'],.75)
        self.assertEqual(r['recovery']['http_success_rate'],1)
if __name__=='__main__':unittest.main()
