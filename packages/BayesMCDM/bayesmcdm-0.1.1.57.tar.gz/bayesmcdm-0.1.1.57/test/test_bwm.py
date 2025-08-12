import numpy as np
from Models.BWM.StandardBWM import StandardBWM
from Models.BWM.GaussianBWM import GaussianBWM
from Models.BWM.TriangularBWM import TriangularBWM
from Models.BWM.IntervalBWM import IntervalBWM

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

def run_standard_bwm(a_b, a_w, cNo, altMat):
    print("\n--- StandardBWM ---")
    for crit_dep in [False, True]:
        for dm_cluster in [-1,2]:
            opt = {'CriteriaDependence': crit_dep, 'Sigma': np.eye(cNo)}
            print(f"CriteriaDependence={crit_dep}")
            bwm = StandardBWM(AB=a_b*100, AW=a_w*100, opt=opt, alternatives=altMat, dm_cluster_number=dm_cluster, 
                              num_samples=num_samples, num_chain=num_chains)
            bwm.sampling()
    print("StandardBWM run complete.")

def run_gaussian_bwm(a_b, a_w, cNo, altMat):
    print("\n--- GaussianBWM ---")
    for crit_dep in [False, True]:
        for dm_cluster in [-1, 2]:
            opt = {'CriteriaDependence': crit_dep, 'Sigma': np.eye(cNo)}
            print(f"CriteriaDependence={crit_dep}")
            bwm = GaussianBWM(
                AB_md=a_b, AB_sigma=0.01*np.ones(a_b.shape),
                AW_md=a_w, AW_sigma=0.01*np.ones(a_w.shape),
                opt=opt, alternatives=altMat, dm_cluster_number=dm_cluster, 
                num_samples=num_samples, num_chain=num_chains
            )
            bwm.sampling()
        print("GaussianBWM run complete.")

def run_triangular_bwm(a_b, a_w, cNo, altMat):
    print("\n--- TriangularBWM ---")
    for crit_dep in [True, False]:
        for dm_cluster in [-1, 2]:
            opt = {'CriteriaIndependence': crit_dep}
            print(f"CriteriaIndependence={crit_dep}")
            bwm = TriangularBWM(AB_md=a_b, AW_md=a_w, opt=opt,  dm_cluster_number=dm_cluster,
                                num_samples=num_samples, num_chain=num_chains)
            bwm.sampling()
    print("TriangularBWM run complete.")

def run_interval_bwm(a_b, a_w, cNo, altMat):
    print("\n--- IntervalBWM ---")
    for crit_dep in [True, False]:
        for dm_cluster in [-1, 2]:
            opt = {'CriteriaDependence': crit_dep}
            print(f"CriteriaDependence={crit_dep}")
            bwm = IntervalBWM(
                AB_l=a_b, AB_h=a_b, AW_l=a_w, AW_h=a_w, opt=opt, 
                dm_cluster_number=dm_cluster,
                num_samples=num_samples, num_chain=num_chains
            )
            bwm.sampling()
        print("IntervalBWM run complete.")

if __name__ == "__main__":
    a_b, a_w, dmNo, cNo, altMat = get_example_data()
    run_standard_bwm(a_b, a_w, cNo, altMat)
    run_gaussian_bwm(a_b, a_w, cNo, altMat) # dependece model for clustering does not work yet
    run_triangular_bwm(a_b, a_w, cNo, altMat)
    run_interval_bwm(a_b, a_w, cNo, altMat)
    print("\nAll BWM model runs completed.")