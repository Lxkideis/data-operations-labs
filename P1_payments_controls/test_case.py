import sqlite3,unittest
from run import generate,reconcile

class ReconciliationTests(unittest.TestCase):
    def test_seeded_errors_are_all_classified(self):
        c=sqlite3.connect(':memory:');generate(c);rows=reconcile(c)
        from collections import Counter
        self.assertEqual(Counter(r[4] for r in rows),{'matched':9800,'missing':50,'duplicate':50,'currency':50,'amount':50,'orphan':10})
        self.assertEqual(len({r[0] for r in rows}),10010)
    def test_currency_does_not_match_on_equal_amount(self):
        c=sqlite3.connect(':memory:');generate(c,0)
        c.execute("INSERT INTO payments VALUES('x','SGD',100,1,'A')")
        c.execute("INSERT INTO settlements VALUES('x','USD',110,10)")
        self.assertEqual(next(r for r in reconcile(c) if r[0]=='x')[4],'currency')

if __name__=='__main__':unittest.main()
