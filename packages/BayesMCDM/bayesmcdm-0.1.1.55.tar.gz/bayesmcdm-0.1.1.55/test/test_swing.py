import numpy as np
from Models.SWING.StandardSWING import StandardSWING
from Models.SWING.GaussianSWING import GaussianSWING
from Models.SWING.TriangularSWING import TriangularSWING
from Models.SWING.IntervalSWING import IntervalSWING

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import logging
logging.getLogger("httpstan").setLevel(logging.ERROR)


num_samples = 200
num_chains = 2

def get_example_data():
    a_b = np.array([
        [3, 4, 6, 1, 5, 2, 9, 7],
        [1, 2, 8, 4, 5, 3, 9, 6],
        [2, 2, 3, 1, 5, 5, 9, 8],
        [2, 1, 8, 2, 9, 3, 8, 8],
        [2, 4, 9, 1, 4, 3, 5, 5],
        [1, 2, 9, 1, 3, 5, 5, 4]
    ])
    a_w = np.array([
        [7, 6, 4, 9, 5, 8, 1, 3],
        [9, 8, 2, 5, 4, 5, 1, 3],
        [8, 8, 5, 9, 5, 5, 1, 2],
        [8, 9, 2, 8, 1, 8, 2, 2],
        [8, 6, 1, 9, 6, 7, 4, 4],
        [9, 8, 1, 9, 7, 5, 5, 6]
    ])
    dmNo, cNo = a_w.shape
    altNo = 50
    x = np.random.rand(altNo // 2, cNo)
    altMat = np.concatenate([x, x * 1])
    return a_b, a_w, dmNo, cNo, altMat

def run_standard_swing(a_b, a_w, cNo, altMat):
    print("\n--- StandardSWING ---")
    for crit_dep in [False]:
        for dm_cluster in [-1,2]:
            opt = {'CriteriaDependence': crit_dep, 'Sigma': np.eye(cNo)}
            print(f"CriteriaDependence={crit_dep}")
            swing = StandardSWING(Prf=a_b*100, opt=opt, alternatives=altMat, dm_cluster_number=dm_cluster, 
                              num_samples=num_samples, num_chain=num_chains)
            swing.sampling()
    print("StandardSWING run complete.")

def run_gaussian_swing(prf, cNo, altMat):
    print("\n--- GaussianSWING ---")
    for crit_dep in [False]:
        for dm_cluster in [-1, 2]:
            opt = {'CriteriaDependence': crit_dep, 'Sigma': np.eye(cNo)}
            print(f"CriteriaDependence={crit_dep}")
            swing = GaussianSWING(
                Prf_md=prf*100, Prf_sigma=0.01*np.ones(a_b.shape),
                opt=opt, alternatives=altMat, dm_cluster_number=dm_cluster, 
                num_samples=num_samples, num_chain=num_chains
            )
            swing.sampling()
        print("GaussianSWING run complete.")

def run_triangular_swing(a_b, a_w, cNo, altMat):
    print("\n--- TriangularSWING ---")
    for crit_dep in [False]:
        for dm_cluster in [-1, 2]:
            opt = {'CriteriaIndependence': crit_dep}
            print(f"CriteriaIndependence={crit_dep}")
            swing = TriangularSWING(Prf_md=a_b, opt=opt,  dm_cluster_number=dm_cluster,
                                num_samples=num_samples, num_chain=num_chains)
            swing.sampling()
    print("TriangularSWING run complete.")

def run_interval_swing(a_b, a_w, cNo, altMat):
    print("\n--- IntervalSWING ---")
    for crit_dep in [False]:
        for dm_cluster in [-1, 2]:
            opt = {'CriteriaDependence': crit_dep}
            print(f"CriteriaDependence={crit_dep}")
            swing = IntervalSWING(
                Prf_l=a_b, Prf_h=a_b, opt=opt, 
                dm_cluster_number=dm_cluster,
                num_samples=num_samples, num_chain=num_chains
            )
            swing.sampling()
        print("IntervalSWING run complete.")

if __name__ == "__main__":
    a_b, a_w, dmNo, cNo, altMat = get_example_data()
    #run_standard_swing(a_b, a_w, cNo, altMat)
    #run_gaussian_swing(a_w, cNo, altMat) # dependece model for clustering does not work yet
    #run_triangular_swing(a_b, a_w, cNo, altMat)
    run_interval_swing(a_b, a_w, cNo, altMat)
    print("\nAll SWING model runs completed.")