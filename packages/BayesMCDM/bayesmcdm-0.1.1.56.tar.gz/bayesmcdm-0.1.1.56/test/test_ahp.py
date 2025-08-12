import numpy as np
from Models.AHP.StandardAHP import StandardAHP
from Models.AHP.IntervalAHP import IntervalAHP
from Models.AHP.GaussianAHP import GaussianAHP
from Models.AHP.TriangularAHP import TriangularAHP

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import logging
logging.getLogger("httpstan").setLevel(logging.ERROR)

num_samples = 200
num_chains = 2

def get_pcm_data():
    PCM =  np.array([
        [
            [1,   3,   5,     4, 7],
            [1/3, 1,   3,     2, 5],
            [1/5, 1/3, 1,   1/2, 3],
            [1/4, 1/2,   2,   1, 3],
            [1/7, 1/5, 1/3, 1/3, 1],
        ],
        [
            [1,     4,   3,    5,  8],
            [1/4,   1,   4,    3,  6],
            [1/3, 1/4,   1,    1,  5],
            [1/5, 1/3,   1,    1,  7],
            [1/8, 1/6, 1/5,  1/7,  1],
        ],
        [
            [1,   1/2,   3,   2,  5],
            [2,     1,   5,   1,  2],
            [1/3, 1/5,   1,   2,  1/2],
            [1/2,   1, 1/2,   1,  5],
            [1/5, 1/2,   2, 1/5,  1], 
        ],
        [
            [1,      3,   5,  2,  6],
            [1/3,    1,   1,  3,  2],
            [1/5,    1,   1,  4,  5],
            [1/2,  1/3, 1/4,  1,  1/2],
            [1/6,  1/2, 1/5,  2,  1],
        ],
        [
            [1,     2, 6,   3,   3],
            [1/2,   1, 2,   5,   4],
            [1/6, 1/2, 1, 1/2,   1],
            [1/3, 1/5, 2,   1,   5],
            [1/3, 1/4, 1, 1/5,   1],
        ],
        [
            [1,     2,   5,   4, 9],
            [1/2,   1,   3,   2, 6],
            [1/5, 1/3,   1,   1, 2],
            [1/4, 1/2,   1,   1, 3],
            [1/9, 1/6, 1/2, 1/3, 1],
        ]
    ])
    return PCM


def run_all_ahp_models(PCM):
    models = [
        #("StandardAHP", StandardAHP),
        #("IntervalAHP", IntervalAHP),
        #("GaussianAHP", GaussianAHP),
        ("TriangularAHP", TriangularAHP)
    ]
    for model_name, model_class in models:
        print(f"\n--- {model_name} ---")
        for crit_dep in [False]:  # , True
            for dm_cluster in [-1, 2]:
                opt = {'CriteriaDependence': crit_dep}
                print(f"CriteriaDependence={crit_dep}, dm_cluster_number={dm_cluster}")
                if model_name == "IntervalAHP":
                    ahp = model_class(
                        PCM_l=PCM,
                        PCM_h=PCM,
                        opt=opt,
                        dm_cluster_number=dm_cluster,
                        num_samples=num_samples,
                        num_chain=num_chains
                    )
                elif model_name == "GaussianAHP":
                    ahp = model_class(
                        PCM_md=PCM,
                        PCM_sigma=0.01 * np.ones_like(PCM),
                        opt=opt,
                        dm_cluster_number=dm_cluster,
                        num_samples=num_samples,
                        num_chain=num_chains
                    )
                elif model_name == "TriangularAHP":
                    ahp = model_class(
                        PCM_md=PCM,
                        opt=opt,
                        dm_cluster_number=dm_cluster,
                        num_samples=num_samples,
                        num_chain=num_chains
                    )
                elif model_name == "StandardAHP":
                    ahp = model_class(
                        PCM=PCM,
                        opt=opt,
                        dm_cluster_number=dm_cluster,
                        num_samples=num_samples,
                        num_chain=num_chains
                    )

                ahp.sampling()
        print(f"{model_name} run complete.")
        print(f"{model_name} run complete.")

if __name__ == "__main__":
    PCM = get_pcm_data()
    run_all_ahp_models(PCM)
    print("\nAll AHP model runs completed.")