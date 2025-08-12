from ..MCDMProblem import MCDMProblem
from .StandardBWM import StandardBWM
import numpy as np

class GaussianBWM(StandardBWM, MCDMProblem):
    
    _basic_model = """
        data { 
            int<lower=2> CNo;
            int<lower=1> DmNo;  
            array[DmNo] vector[CNo] AB_md; 
            array[DmNo] vector[CNo] AW_md; 
            array[DmNo] vector[CNo] AB_sigma; 
            array[DmNo] vector[CNo] AW_sigma; 
            vector<lower=0,upper=1>[CNo] e;
            real<lower=0.0001> gamma_param; // prior for the Gamma distribution
        } 

        parameters {             
            simplex[CNo] wStar;
            real<lower=0> kappaStar;

            array[DmNo] simplex[CNo] W;
            array[DmNo] real<lower=0> kappa;

            array[DmNo] vector<lower=0>[CNo] AW;
            array[DmNo] vector<lower=0>[CNo] AB;
        } 

        transformed parameters {
            array[DmNo] simplex[CNo] AB_normalized;
            array[DmNo] simplex[CNo] AW_normalized;

            for(i in 1:DmNo) {
                AB_normalized[i] = (e ./ AB[i]) ./ sum(e ./ AB[i]);
                AW_normalized[i] = AW[i] ./ sum(AW[i]);       
            }
        }

        model {
            kappaStar ~ gamma(gamma_param,gamma_param);
            wStar ~ dirichlet(0.01*e);
            
            for (i in 1:DmNo){
                kappa[i] ~ gamma(gamma_param,gamma_param);
                W[i] ~ dirichlet(kappaStar*wStar);

                for(j in 1:CNo){
                    AB_md[i,j] ~ normal(AB[i,j], 0.1*AB_sigma[i,j]);
                    AW_md[i,j] ~ normal(AW[i,j], 0.1*AW_sigma[i,j]);
                }

                AW_normalized[i] ~ dirichlet(kappa[i]*W[i]);
                AB_normalized[i] ~ dirichlet(kappa[i]*W[i]);    
            }
        } 
    """

    _basic_model_clustering = """
        data { 
            int<lower=2> CNo;
            int<lower=1> DmNo;  
            array[DmNo] vector[CNo] AB_md; 
            array[DmNo] vector[CNo] AW_md; 
            array[DmNo] vector[CNo] AB_sigma; 
            array[DmNo] vector[CNo] AW_sigma; 
            vector<lower=0,upper=1>[CNo] e;

            int<lower=2> DmC;
            real<lower=0.0001> gamma_param; // prior for the Gamma distribution
        } 

        parameters { 
            array[DmNo] simplex[CNo] W;
            array[DmNo] real<lower=0> kappa;

            array[DmC] simplex[CNo] wc;
            array[DmC] real<lower=0> ksi; 
            array[DmNo] simplex[DmC] theta;

            array[DmNo] vector<lower=0>[CNo] AW;
            array[DmNo] vector<lower=0>[CNo] AB;
        } 

        transformed parameters {
            array[DmNo] simplex[CNo] AB_normalized;
            array[DmNo] simplex[CNo] AW_normalized;

            for(i in 1:DmNo){
                AB_normalized[i] = (e ./ AB[i]) ./ sum(e ./ AB[i]); 
                AW_normalized[i] = AW[i] ./ sum(AW[i]);
            }
        }

        model {      
            for(i in 1:DmC){
                wc[i] ~ dirichlet(0.01*e);
                ksi[i] ~ gamma(gamma_param,gamma_param);
            }

            for (i in 1:DmNo){
                array[DmC] real contribution;
                for(j in 1:DmC)
                     contribution[j] = log(theta[i,j]) + dirichlet_lpdf( W[i] | ksi[j]*wc[j]);
                target += log_sum_exp(contribution);

                for(j in 1:CNo){
                    AB_md[i,j] ~ normal(AB[i,j], AB_sigma[i,j]);
                    AW_md[i,j] ~ normal(AW[i,j], AW_sigma[i,j]);
                }
                kappa[i] ~ gamma(gamma_param,gamma_param);
                AW_normalized[i] ~ dirichlet(kappa[i]*W[i]);
                AB_normalized[i] ~ dirichlet(kappa[i]*W[i]);    
        }
    } 
    """
    
    _basic_model_sorting = """
        data { 
            int<lower=2> CNo;
            int<lower=1> DmNo;  
            array[DmNo] vector[CNo] AB_md; 
            array[DmNo] vector[CNo] AW_md; 
            array[DmNo] vector[CNo] AB_sigma; 
            array[DmNo] vector[CNo] AW_sigma; 
            vector<lower=0,upper=1>[CNo] e;

            int<lower=2> AltNo;
            int<lower=2> AltC;
            matrix[AltNo, CNo] Alt;
        } 

        parameters { 
            array[DmNo] simplex[CNo] W;
            array[DmNo] real<lower=0> kappa;

            simplex[CNo] wStar;
            real<lower=0> kappaStar;

            vector[AltC] altMu;

            array[DmNo] vector<lower=0>[CNo] AW;
            array[DmNo] vector<lower=0>[CNo] AB;
        } 

        transformed parameters {
            array[DmNo] simplex[CNo] AB_normalized;
            array[DmNo] simplex[CNo] AW_normalized;

            for(i in 1:DmNo){
                AB_normalized[i] = (e ./ AB[i]) ./ sum(e ./ AB[i]); 
                AW_normalized[i] = AW[i] ./ sum(AW[i]);
            }

            vector[AltNo] v = Alt * wStar;
            v ./= (1-v);
            v = log(v);
            array[AltNo, AltC] real<upper=0> soft_z; // log unnormalized clusters
            
            for (n in 1:AltNo)
                for (k in 1:AltC)
                    soft_z[n, k] = -log(AltC) - 0.5 * pow(altMu[k] - v[n],2);        
        }

        model {
            kappaStar ~ gamma(.01,.01);
            wStar ~ dirichlet(0.01*e);

            W ~ dirichlet(kappaStar*wStar);
            kappa ~ gamma(.01,.01);
            
            for (i in 1:DmNo){
                AB_md[i] ~ normal(AB[i], AB_sigma[i]);
                AW_md[i] ~ normal(AW[i], AW_sigma[i]);

                AW_normalized[i] ~ dirichlet(kappa[i]*W[i]);
                AB_normalized[i] ~ dirichlet(kappa[i]*W[i]);    
            }

            for (n in 1:AltNo)
                target += log_sum_exp(soft_z[n]);

        } 
    """
    
    _correlated_model = """
        data { 
            int<lower=2> CNo;
            int<lower=1> DmNo;  
            array[DmNo] vector[CNo] AB_md; 
            array[DmNo] vector[CNo] AW_md; 
            array[DmNo] vector[CNo] AB_sigma; 
            array[DmNo] vector[CNo] AW_sigma; 
            vector<lower=0,upper=1>[CNo] e;

            vector[CNo] mu; // mean of unnormalized weight
            cov_matrix[CNo] Sigma;

            real<lower=0.0001> gamma_param; // prior for the Gamma distribution
            real<lower=0.001> sigma_coef; // coefficient for the covariance matrix
        } 

        parameters { 
            array[DmNo] vector[CNo] W_eta; 
            vector[CNo] wStar_eta;
            array[DmNo] real<lower=0> kappa;

            array[DmNo] vector<lower=0>[CNo] AB; 
            array[DmNo] vector<lower=0>[CNo] AW;
        } 

        transformed parameters {
            array[DmNo] simplex[CNo] AB_normalized;
            array[DmNo] simplex[CNo] AW_normalized;

            for(i in 1:DmNo){
                AB_normalized[i] = (e ./ AB[i]) ./ sum(e ./ AB[i]); 
                AW_normalized[i] = AW[i] ./ sum(AW[i]);
            }

            array[DmNo] simplex[CNo] W;
            simplex[CNo] wStar;

            wStar = softmax(wStar_eta);
            
            for(i in 1:DmNo)
                W[i] = softmax(W_eta[i]);
        } 

        model {
            wStar_eta ~ multi_normal(mu, Sigma);

            for (i in 1:DmNo){
                W_eta[i] ~ multi_normal(wStar_eta, Sigma);

                AB_md[i] ~ normal(AB[i], AB_sigma[i]);
                AW_md[i] ~ normal(AW[i], AW_sigma[i]);

                kappa[i] ~ gamma(gamma_param,gamma_param);
                AW_normalized[i] ~ dirichlet(kappa[i]*W[i]);
                AB_normalized[i] ~ dirichlet(kappa[i]*W[i]);    
            }
        }
    """

    _correlated_model_clustering = """
        data { 
            int<lower=2> CNo;
            int<lower=1> DmNo;  
            array[DmNo] vector[CNo] AB_md; 
            array[DmNo] vector[CNo] AW_md; 
            array[DmNo] vector[CNo] AB_sigma; 
            array[DmNo] vector[CNo] AW_sigma; 
            vector<lower=0,upper=1>[CNo] e;

            int<lower=2> DmC;

            vector[CNo] mu; // mean of unnormalized weight
            cov_matrix[CNo] Sigma;

            real<lower=0.0001> gamma_param; // prior for the Gamma distribution
            real<lower=0.001> sigma_coef; // coefficient for the covariance matrix
        } 

        parameters { 
            array[DmNo] vector[CNo] W_eta;
            array[DmNo] real<lower=0> kappa;

            array[DmNo] simplex[DmC] theta;
            array[DmC] vector[CNo] wc_eta;


            array[DmNo] vector<lower=0>[CNo] AB;
            array[DmNo] vector<lower=0>[CNo] AW;
        }

        transformed parameters {
            array[DmNo] simplex[CNo] AB_normalized;
            array[DmNo] simplex[CNo] AW_normalized;

            for(i in 1:DmNo){
                AB_normalized[i] = (e ./ AB[i]) ./ sum(e ./ AB[i]); 
                AW_normalized[i] = AW[i] ./ sum(AW[i]);
            }

            array[DmNo] simplex[CNo] W;
            array[DmC] simplex[CNo] wc;

            for(i in 1:DmNo)
                W[i] = softmax(W_eta[i]);
            
            for(i in 1:DmC)
                wc[i] = softmax(wc_eta[i]);  
        } 

        model {
            for (i in 1:DmC)
                wc_eta[i] ~ multi_normal(mu, Sigma);
 
            for (i in 1:DmNo) {     
                array[DmC] real contribution; 
                for(j in 1:DmC)
                    contribution[j] = log(theta[i,j]) + multi_normal_lpdf( W_eta[i] | wc_eta[j], Sigma*sigma_coef);
                target += log_sum_exp(contribution);   

                AB_md[i] ~ normal(AB[i], AB_sigma[i]);
                AW_md[i] ~ normal(AW[i], AW_sigma[i]);

                kappa[i] ~ gamma(gamma_param,gamma_param);
                AW_normalized[i] ~ dirichlet(kappa[i]*W[i]);
                AB_normalized[i] ~ dirichlet(kappa[i]*W[i]);    
            }
        }
    """

    _correlated_model_sorting = """
        data { 
            int<lower=2> CNo;
            int<lower=1> DmNo;  
            array[DmNo] vector[CNo] AB_md; 
            array[DmNo] vector[CNo] AW_md; 
            array[DmNo] vector[CNo] AB_sigma; 
            array[DmNo] vector[CNo] AW_sigma; 
            vector<lower=0,upper=1>[CNo] e;

            int<lower=2> AltNo;
            matrix[AltNo, CNo] Alt;
            int<lower=2> AltC;
            vector<lower=0,upper=1>[AltC] eAlt;

            vector[CNo] mu; // mean of unnormalized weight
            cov_matrix[CNo] Sigma;
        } 

        parameters { 
            array[DmNo] vector[CNo] W_eta; 
            vector[CNo] wStar_eta;
            real<lower=0> kappaStar;  
            array[DmNo] real<lower=0> kappa;

            vector[AltC] altMu;

            array[DmNo] vector<lower=0>[CNo] AB;
            array[DmNo] vector<lower=0>[CNo] AW;
        } 

        transformed parameters {
            array[DmNo] simplex[CNo] AB_normalized;
            array[DmNo] simplex[CNo] AW_normalized;

            for(i in 1:DmNo){
                AB_normalized[i] = (e ./ AB[i]) ./ sum(e ./ AB[i]); 
                AW_normalized[i] = AW[i] ./ sum(AW[i]);
            }

            array[DmNo] simplex[CNo] W;
            simplex[CNo] wStar;

            wStar = softmax(wStar_eta);
            
            for(i in 1:DmNo) {
                W[i] = softmax(W_eta[i]);
            }

            vector[AltNo] v = Alt * wStar;
            v ./= (1-v);
            v = log(v);
            array[AltNo, AltC] real<upper=0> soft_z; // log unnormalized clusters
            for (n in 1:AltNo)
                for (k in 1:AltC)
                    soft_z[n, k] = -log(AltC) - 0.5 * pow(altMu[k] - v[n],2);
                
        } 

        model {
            wStar_eta ~ multi_normal(mu, Sigma);
            kappa ~ gamma(.01,.01);
                            
            for (i in 1:DmNo){
                W_eta[i] ~ multi_normal(wStar_eta, Sigma);

                AB_md[i] ~ normal(AB[i], AB_sigma[i]);
                AW_md[i] ~ normal(AW[i], AW_sigma[i]);

                AW_normalized[i] ~ dirichlet(kappa[i]*W[i]);
                AB_normalized[i] ~ dirichlet(kappa[i]*W[i]);    
            }

            for (n in 1:AltNo)
               target += log_sum_exp(soft_z[n]);
        }
    """

    def __init__(self, AB_md, AW_md, AB_sigma, AW_sigma, alternatives = None, dm_cluster_number=-1, alt_sort_number=-1, num_chain=3, num_samples=1000, opt={}):
        self.AB_MD = np.array(AB_md)
        self.AW_MD = np.array(AW_md)
        self.AB_Sigma = np.array(AB_sigma)
        self.AW_Sigma = np.array(AW_sigma)

        MCDMProblem.__init__(self, alternatives, dm_cluster_number, alt_sort_number, num_chain, num_samples,opt)

    @property
    def input_data(self):
        data = self._get_common_data()
        data['AW_md'] = self.AW_MD
        data['AW_sigma'] = self.AW_Sigma
        data['AB_md'] = self.AB_MD
        data['AB_sigma'] = self.AB_Sigma
        data['e'] =  np.ones(self.criteria_no)
        return data

    @property
    def dm_no(self):
        return self.AB_MD.shape[0]
    
    @property
    def criteria_no(self):
        return self.AB_MD.shape[1]

    def _check_input_data(self):
        assert self.AB_MD.shape == self.AB_Sigma.shape, "AB_MD and AB_Sigma must be of the same size!"
        assert self.AW_MD.shape == self.AW_Sigma.shape, "AW_MD and AW_Sigma must be of the same size!"
        assert self.AB_MD.shape == self.AW_MD.shape, "AB and AW (mean and standard deviation) must be of the same size!"

        assert self.AB_MD.shape[0] >=1, "No input"
        assert self.AW_MD.shape[1] >=2, "The number of criteria must be more than 2!"

        return True


if __name__ == "__main__":
    a_b =  np.array([
       [ 3, 4, 6, 1, 5, 2, 9, 7],
       [ 1, 2, 8, 4, 5, 3, 9, 6],
       [ 2, 2, 3, 1, 5, 5, 9, 8],
       [ 2, 1, 8, 2, 9, 3, 8, 8],
       [ 2, 4, 9, 1, 4, 3, 5, 5],
       [ 1, 2, 9, 1, 3, 5, 5, 4]])

    a_w =  np.array([
        [ 7, 6, 4, 9, 5, 8, 1, 3],
        [ 9, 8, 2, 5, 4, 5, 1, 3],
        [ 8, 8, 5, 9, 5, 5, 1, 2],
        [ 8, 9, 2, 8, 1, 8, 2, 2],
        [ 8, 6, 1, 9, 6, 7, 4, 4],
        [ 9, 8, 1, 9, 7, 5, 5, 6]]) 

    dmNo, cNo = a_w.shape
    altNo = 50
    x = np.random.rand(altNo // 2, cNo)
    altMat = np.concatenate([x*1,x])

    opt = {'CriteriaDependence': False}

    bwm = GaussianBWM(AB_md= a_b, AB_sigma=0.01*np.ones(a_b.shape), AW_md=a_w, AW_sigma=0.01*np.ones(a_w.shape), opt=opt, alternatives=altMat, alt_sort_number=2)
    bwm.sampling()
    print('Ok')
        