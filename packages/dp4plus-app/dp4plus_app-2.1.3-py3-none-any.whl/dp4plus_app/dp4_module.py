# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 05:05:52 2022

@author: Franco, Bruno Agustín 


DP4+ calculation module
The algorithm uses simple matrix operations, optimizing the calculation 
processes. To do this, separate each stage of the general formula of the DP4+ 
method.
For correlation of experimental data, it uses an auxiliary module 
nmr_correl_module, leaving only the statistical part here. For more info 
read nmr_correl_module documentation
"""
import glob
import pandas as pd
import numpy as np
import scipy.stats as st

from sklearn import linear_model

#AGREGAR RELATIVE PATH PARA QUE ANDE EN PYPI
from . import correlation_module as nmr_correl


def get_uns_shifts(tens_matrix, nucl_type, standard):
    '''Calculate the unscaled chemical shifts as the diference of the 
    standard tensor and each nucleus tensor. Returns a np.array() matrix
    '''
    uns = np.empty(tens_matrix.shape)
    uns[:] = np.nan
    
    uns[nucl_type['C']] = standard['C'] - tens_matrix[nucl_type['C']]
    uns[nucl_type['H']] = standard['H'] - tens_matrix[nucl_type['H']]
    
    return uns

def get_sca_shifts(uns_matrix, nucl_type, exp_data):
    '''Calculate the scaled chemical shifts. 
    Generates the linear regression between the unscaled matrix and the 
    experimental data to obtain the slope and ordinate. Then, these are used 
    to extrapolate the scaled chemical shifts.
    Returns a np.array() matrix.
    '''
    sca = np.empty(uns_matrix.shape)
    sca[:] = np.nan
    
    #invoco al modelo de regresión
    #el mismo se reutiliza para C y para H. Por eso h y m son genéricas
    regresion = linear_model.LinearRegression()
    
    for i,isom_uns in enumerate(uns_matrix.T):

        #Para C
        if len (isom_uns[nucl_type['C']]) > 1: 
            regresion.fit(exp_data[nucl_type['C']][['exp_data']], 
                          isom_uns[nucl_type['C']]) 
            m = regresion.coef_        #pendientes ,devuelve array pensando q es multivariada
            b = regresion.intercept_    #intercección    
            sca[nucl_type['C'],i] = (isom_uns[nucl_type['C']] - b) / m [0]
        
            print (f'Reg C : uns x {m} + {b}')
        else : 
            sca[nucl_type['C'],i] = (isom_uns[nucl_type['C']])
            
        print (isom_uns[nucl_type['C']])
        
        if len (isom_uns[nucl_type['H']]) > 1 :
            #Para H
            regresion.fit(exp_data[nucl_type['H']][['exp_data']], 
                          isom_uns[nucl_type['H']]) 
            m = regresion.coef_        #pendientes ,devuelve array pensando q es multivariada
            b = regresion.intercept_    #intercección    
            sca[nucl_type['H'],i] = (isom_uns[nucl_type['H']] - b) / m [0]
            
            print (isom_uns[nucl_type['H']])
            
        else: 
            sca[nucl_type['H'],i] = (isom_uns[nucl_type['H']])
            
        print (f'Reg H : uns x {m} + {b}')

    return sca

def calc_errors(matrix,exp_data): 
    '''calculates the differences between experimental data and a chemical 
    shift matrix. That is, the errors. 
    '''
    errors = np.empty(matrix.shape)
    for i,isom in enumerate(matrix.T):
        errors[:,i] = matrix[:,i] - exp_data['exp_data']
        
    return errors

def calc_prob_matr(uns, sca, nucl_type, parameters):
    '''Using the t-student distribution parameters, calculates the INDIVIDUAL 
    probabilities of each nucleus. Therefore, the answer is a probability 
    matrix (np.array)
    Since each level has 6 nucleus types, a helper function is used to 
    compute the probabilities for each set (single_t_prob).
    '''
    uns_p = np.empty(uns.shape) 
    uns_p[nucl_type['H_sp2']] = single_t_prob(uns[nucl_type['H_sp2']],
                                              parameters.loc['Hsp2'])
    uns_p[nucl_type['H_sp3']] = single_t_prob(uns[nucl_type['H_sp3']],
                                              parameters.loc['Hsp3'])
    uns_p[nucl_type['C_sp2']] = single_t_prob(uns[nucl_type['C_sp2']],
                                              parameters.loc['Csp2'])
    uns_p[nucl_type['C_sp3']] = single_t_prob(uns[nucl_type['C_sp3']],
                                              parameters.loc['Csp3'])
    
    sca_p = np.empty(uns.shape) 
    sca_p[nucl_type['H']] = single_t_prob(sca[nucl_type['H']],
                                              parameters.loc['Hsca'])
    sca_p[nucl_type['C']] = single_t_prob(sca[nucl_type['C']],
                                              parameters.loc['Csca'])
    
    return uns_p, sca_p

def single_t_prob(array , t_param):
    '''Using the given distribution parameters, compute the t student 
    probability of each element in a matrix. In this case calculates the 
    chemical shift errors probabilities.
    '''
    t_dist = st.t(t_param['n'])  #ajuste de la distribución     
    array = abs ((array - t_param['m'])/t_param['s'])
    prob = 1 - t_dist.cdf(array)
    return prob

def calc_results(uns_p, sca_p, nucl_type, isomer_list): 
    '''Generates the final results of DP4+
    The column product is applied to each probability matrix to obtain the 
    absolute probability of each isomer. 
    Then, the final probabilities are obtained by means of the aboslute 
    probability of all the candidates
    '''
    p_abs = pd.DataFrame(columns=isomer_list)
    
    for nuclei in ['C','H']:
        p_abs.loc[f'{nuclei}_uns'] = np.prod(uns_p[nucl_type[nuclei]],axis=0)
        p_abs.loc[f'{nuclei}_sca'] = np.prod(sca_p[nucl_type[nuclei]],axis=0)
        p_abs.loc[f'{nuclei}_full'] = p_abs.loc[f'{nuclei}_uns']*p_abs.loc[f'{nuclei}_sca']
    
    p_abs.loc['Uns'] = p_abs.loc['H_uns']*p_abs.loc['C_uns']
    p_abs.loc['Sca'] = p_abs.loc['H_sca']*p_abs.loc['C_sca']
    p_abs.loc['Full'] = p_abs.loc['C_full']*p_abs.loc['H_full']   
    
    p_rel = pd.DataFrame(columns=isomer_list)
    for p_type, vector in p_abs.iterrows():
        p_rel.loc[p_type] = vector/np.sum(vector)
    
    return p_rel
    #return p_rel.sort_index(ascending=True)
    

def calc (isom_list, nmr_fold, xlsx, use_energy, energy_info, standard, parameters ):
    '''Main function of the module
    Contains the main calculation algorithm of DP4+.
    Following the step by step, the calculation method used can be understood.
    '''
    
    exp_data, wtl = nmr_correl.get_exp_data(xlsx, 
                                            sheet='shifts', 
                                            isom_list=isom_list)
    df_selections = nmr_correl.selections(exp_data)
    
    tens_by_conf_a_isom = nmr_correl.collect_G09_data(isom_list, nmr_fold, 
                                                      use_energy, energy_info)
    
    import os
    path = os.path.join(nmr_fold,'..','temp.xlsx')
    mode = 'a' if os.path.exists(path) else 'w'
    with pd.ExcelWriter(path, mode=mode) as writer: 
        for isom, df in tens_by_conf_a_isom.items():
            df.to_excel(writer,sheet_name = isom)
    
    tens_by_isom = {}
    for isom, tens_by_conf in tens_by_conf_a_isom.items():
        tens_by_isom[isom] = nmr_correl.Boltzman_pond (tens_by_conf) 
          
    # tens_by_isom = pd.DataFrame(tens_by_isom)
    # tens_by_isom.to_excel(os.path.join(nmr_fold,'temp.xlsx'),sheet_name = isom)
    
    tens_by_isom = np.array(list(tens_by_isom.values())).T
    
    # tens = nmr_correl.G09_tens_matrix(isom_list)     
    tens_by_isom_sorted = nmr_correl.sort_tens_matrix(tens_by_isom, isom_list, exp_data, wtl) 
    
    if type(tens_by_isom_sorted) == str : 
        return tens_by_isom_sorted
    
    uns = get_uns_shifts(tens_by_isom_sorted,df_selections, standard )
    sca = get_sca_shifts(uns, df_selections, exp_data)
        
    uns_e = calc_errors(uns,exp_data)
    sca_e = calc_errors(sca,exp_data)
    
    uns_p, sca_p = calc_prob_matr (uns_e, sca_e, df_selections, parameters)
        
    results = calc_results(uns_p, sca_p, df_selections, isom_list)
   
    return {'exp': exp_data,
            'results': results,
            'tens' : tens_by_isom_sorted,
            'p_sca': sca_p,
            'd_sca': sca,
            'e_sca': sca_e,
            'p_uns': uns_p,
            'd_uns': uns,
            'e_uns': uns_e}

def isomer_count():
    '''Determine the amount of isomeric candidates to be evaluated
    The files must be named by: isomerID_ * .log 
    '''    
    files = []
    for file in glob.glob('*'): 
        if ('nmr' in file.casefold() and 
            any(extention in file[-4:] for extention in ['.out','.log'])): 
            files.append(file)
    
    isomer_list =[]
    for file in files:
        if file.split('_',1)[0] not in isomer_list:
            isomer_list.append(file.split('_',1)[0])
        else:
            continue
    isomer_list.sort() ##RG
    isomer_list.sort(key=lambda s: len(s)) #RG    
    return isomer_list, len(isomer_list)


