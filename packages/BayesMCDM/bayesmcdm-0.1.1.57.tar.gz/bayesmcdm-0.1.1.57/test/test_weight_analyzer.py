import sys
import os
sys.path.append(os.path.abspath("src"))

import numpy as np
from BayesMCDM import WeightAnalyzer

if __name__ == "__main__":
    prf =  np.array([
        [ 7, 6, 4, 9, 5, 8, 1, 3],
        [ 9, 8, 2, 5, 4, 5, 1, 3],
        [ 8, 8, 5, 9, 5, 5, 1, 2],
        [ 8, 9, 2, 8, 1, 8, 2, 2],
        [ 8, 6, 1, 9, 6, 7, 4, 4],
        [ 9, 8, 1, 9, 7, 5, 5, 6],
    ])
    weights = prf / prf.sum(axis=1, keepdims=True)

    dmNo, cNo = prf.shape
    altNo = 50
    x = np.random.rand(altNo // 2, cNo)
    altMat = np.concatenate([x*10,x])

    opt = {'CriteriaDependence': False, 'Sigma': np.eye(cNo) }

    weight_aggregation = WeightAnalyzer.StandardWeightAnalyzer(weights=weights, opt=opt, alternatives=altMat) #, dm_cluster_number=2)
    weight_aggregation.sampling()
    print('Ok')
