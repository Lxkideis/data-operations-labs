import unittest
from run import summarize
class ProcessTests(unittest.TestCase):
    def test_sla_boundary_and_odd_median(self):
        rows=[{'total_hours':h,'queue_hours':1,'rework':0} for h in [1,48,49]]
        r=summarize(rows);self.assertEqual(r['median_hours'],48);self.assertAlmostEqual(r['sla_breach_rate'],1/3,places=4)
if __name__=='__main__':unittest.main()
