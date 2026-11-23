import unittest
import numpy as np
from run import auc,prepare,FEATURES,FORBIDDEN
class ModelTests(unittest.TestCase):
    def test_auc_ties(self):
        self.assertEqual(auc(np.array([0,1]),np.array([.5,.5])),.5)
        self.assertEqual(auc(np.array([0,1]),np.array([.1,.9])),1)
    def test_preprocessing_cannot_learn_from_test(self):
        t=np.array([[1.,2.],[3.,4.]])
        a,median,mean,sd=prepare(t,np.array([[np.nan,6.]]),np.array([[1000.,2000.]]))
        np.testing.assert_array_equal(median,[2,3]);np.testing.assert_array_equal(mean,[2,3])
        self.assertEqual(a[1][0,1],0)
    def test_no_outcome_or_identifiers_in_features(self):
        self.assertFalse(set(FEATURES)&set(FORBIDDEN))
if __name__=='__main__':unittest.main()
