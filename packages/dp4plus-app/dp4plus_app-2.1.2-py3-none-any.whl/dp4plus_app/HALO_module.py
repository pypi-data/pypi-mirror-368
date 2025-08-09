# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 14:55:52 2023

@author: UCA Team
"""

import os
import pandas as pd
import numpy as np

from . import correlation_module as nmr_correl
from . import dp4_module as dp4


def HALO_calc (isom_list, nmr_fold, xlsx, use_energy, energy_info, 
               standard, parameters, MSTD_stand ):
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
     
    # with pd.ExcelWriter(os.path.join(nmr_fold,'..','temp.xlsx')) as writer: 
    #     for isom, df in tens_by_conf_a_isom.items():
    #         df.to_excel(writer,sheet_name = isom)
    
    tens_by_isom = {}
    for isom, tens_by_conf in tens_by_conf_a_isom.items():
        tens_by_isom[isom] = nmr_correl.Boltzman_pond (tens_by_conf) 
          
    # tens_by_isom = pd.DataFrame(tens_by_isom)
    # tens_by_isom.to_excel(os.path.join(nmr_fold,'temp.xlsx'),sheet_name = isom)
    
    tens_by_isom = np.array(list(tens_by_isom.values())).T
    
    # tens = nmr_correl.G09_tens_matrix(isom_list)     
    tens_by_isom_sorted = nmr_correl.sort_tens_matrix(tens_by_isom, 
                                                      isom_list, exp_data, wtl)
    
    if type(tens_by_isom_sorted) == str : 
        return tens_by_isom_sorted
    
    '''-------------------------HALO FUNTIONS-------------------------------'''    
    halogen_col = find_halogen_neigh(wtl, nmr_fold, isom_list)
    
    exp_data = pd.concat([exp_data, halogen_col], axis=1)
    
    df_selections = pd.concat([df_selections, HALO_selections(exp_data)], axis=1)
    
    uns = dp4.get_uns_shifts(tens_by_isom_sorted,df_selections, standard)
    
    # va sobre escribir los desplazamientos con halogenos
    uns = get_MSTD_uns_shifts(tens_by_isom_sorted, df_selections, uns, MSTD_stand)
    
    '''-------------------------END FUNTIONS-------------------------------'''
    
    sca = dp4.get_sca_shifts(uns, df_selections, exp_data)
        
    uns_e = dp4.calc_errors(uns,exp_data)
    sca_e = dp4.calc_errors(sca,exp_data)
    
    uns_p, sca_p = dp4.calc_prob_matr (uns_e, sca_e, df_selections, parameters)
        
    results = dp4.calc_results(uns_p, sca_p, df_selections, isom_list)
   
    return {'exp': exp_data,
            'results': results,
            'tens' : tens_by_isom_sorted,
            #'p_sca': sca_p,
            'd_sca': sca,
            'e_sca': sca_e,
            #'p_uns': uns_p,
            'd_uns': uns,
            'e_uns': uns_e}
      

def HALO_selections(data):
    '''Classify types of nucleis (subsequently erros and probabilities types) 
    analizing the exp_data information. 
    Returns a pd.DataFrame with boolean columns (True or False) that indicates
    which nuclei of any correlated matrix corresponds to that gruoup'''
    selection = pd.DataFrame(columns=['C_Cl_sp2','C_Cl_sp3',
                                      'C_Br_sp2','C_Br_sp3',
                                      'H_Cl_sp2','H_Cl_sp3',
                                      'H_Br_sp2','H_Br_sp3'])
    
    selection ['C_Cl_sp2'] = (data ['nuclei']=='C') & (data ['halogen']=='Cl') & (data ['sp2']==1)
    selection ['C_Cl_sp3'] = (data ['nuclei']=='C') & (data ['halogen']=='Cl') & (data ['sp2']!=1)
    
    selection ['C_Br_sp2'] = (data ['nuclei']=='C') & (data ['halogen']=='Br') & (data ['sp2']==1)
    selection ['C_Br_sp3'] = (data ['nuclei']=='C') & (data ['halogen']=='Br') & (data ['sp2']!=1)
    
    selection ['H_Cl_sp2'] = (data ['nuclei']=='H') & (data ['halogen']=='Cl') & (data ['sp2']==1)
    selection ['H_Cl_sp3'] = (data ['nuclei']=='H') & (data ['halogen']=='Cl') & (data ['sp2']!=1)
    
    selection ['H_Br_sp2'] = (data ['nuclei']=='H') & (data ['halogen']=='Br') & (data ['sp2']==1)
    selection ['H_Br_sp3'] = (data ['nuclei']=='H') & (data ['halogen']=='Br') & (data ['sp2']!=1)
   
    return selection

def get_MSTD_uns_shifts(tens_matrix, nucl_type, uns,  MSTD_stand):
    '''Calculate the unscaled chemical shifts as the diference of the 
    standard tensor and each nucleus tensor. Returns a np.array() matrix
    '''    
    for HALO_type, (std_tens, std_exp) in MSTD_stand.iterrows(): 
        
        uns[nucl_type[HALO_type]] = std_tens - tens_matrix[nucl_type[HALO_type]] + std_exp
    
    return uns

# ---------------------------------------------------------------------------
def find_halogen_neigh(wtl, nmr_dir, isom_list): 
    
    # -------------------------------------------------------------------------
    def extract_coor_matrix (file): 
        with open (file_original,'rt') as f:
            lines=f.readlines()
        
        # encontrar ubicacion de la matriz
        for i, line in enumerate(lines[100:]):
            if 'Standard orientation:' in line: 
                start_line = 100 + i + 5                        
            if 'Rotational constants' in line: 
                end_line = 100 + i -1
                break
        
        # leer la matriz de coord
        coord_mat=[] 
        for line in lines[start_line : end_line]:
            row = line.split()[:]
            row = [float(_) for _ in row]
            coord_mat.append(row) 
        
        return np.array(coord_mat)
    
    # -------------------------------------------------------------------------
    def dist_mat_calculator(coord_mat):
        ''' funcon anidada '''
        coordenates = coord_mat[:,3:6]
        dist_mat = np.zeros([len(coordenates), len(coordenates)])
        for i in range(dist_mat.shape[0]):
            for j in range(i):
                dist_mat[i][j] = np.sqrt(sum(np.power((coordenates[i]-coordenates[j]),2)))

        return dist_mat
    
    # -------------------------------------------------------------------------
    def detect_halogen (dist_mat, coord_mat):
        # Extrae los pesos de los átomos desde la matriz de coordenadas
        pesos = [coord_mat[i][1] for i in range(len(coord_mat))]
        mat_vecinos = dist_mat.copy()
        atoms = len(pesos)
        
        # Lista para almacenar las relaciones de vecindad entre Bromo y Carbono
        C_Br_idx, C_Cl_idx = [], []
        
        for col in range(atoms):
            for row in range(atoms):
                a = dist_mat[row][col]
                # Identifica vecinos en función de los criterios de distancia y tipo de átomo
                if a < 2.1 and a > 0:
                    if (pesos[row] == 35 and pesos[col] == 6):  # Bromo y Carbono
                        C_Br_idx.append(col + 1)
                    elif (pesos[row] == 6 and pesos[col] == 35):  # Carbono y Bromo
                        C_Br_idx.append(row + 1)
                    elif (pesos[row] == 17 and pesos[col] ==6):
                        C_Cl_idx.append(col + 1)
                    elif (pesos[row] == 6 and pesos[col] == 17):
                        C_Cl_idx.append(row + 1)
                # Construcción de la matriz binaria de vecinos para otros casos
                if (a < 2.1 and a > 0 and (pesos[row] > 18 or pesos[col] > 18)) or \
                   (a < 1.8 and a > 0 and (pesos[row] < 18 or pesos[col] < 18)):
                    mat_vecinos[row][col] = 1
                else:
                    mat_vecinos[row][col] = 0
        
        # Hacer simétrica la matriz de vecinos
        mat_transpuesta = np.transpose(mat_vecinos)
        vecinos = mat_vecinos + mat_transpuesta
        
        H_Br_idx, H_Cl_idx = [], []

        for row in range(atoms):
            if pesos[row] == 1:  # Si el átomo es hidrógeno
                for carbono in C_Br_idx:
                    if vecinos[row][carbono - 1] == 1:
                        H_Br_idx.append( row + 1 )
                for carbono in C_Cl_idx:
                    if vecinos[row][carbono - 1] == 1:
                        H_Cl_idx.append( row + 1 )

        
        return C_Br_idx, C_Cl_idx , H_Br_idx, H_Cl_idx
    
    # -------------------------------------------------------------------------    
    def place_halogens_in_wtl(wtl , C_Br_idx, C_Cl_idx, H_Br_idx, H_Cl_idx): 
        '''
        '''
        record = pd.Series([None] * len(wtl), dtype=object) 
        
        for row , labels in enumerate (wtl): # iterar sobre las filas del wtl 
            if any( lab in C_Br_idx for lab in labels ): 
                record[row] = 'Br'
            if any( lab in C_Cl_idx for lab in labels ): 
                record[row] = 'Cl'
            if any( lab in H_Br_idx for lab in labels ): 
                record[row] = 'Br'
            if any( lab in H_Cl_idx for lab in labels ): 
                record[row] = 'Cl'
        
        return record 
                    
    # -------------------------------------------------------------------------                
    '''aca empieza la parte principal de la funcion 
    '''
    
    records = pd.DataFrame()  # acá se irán cargando las etiquetas de los halogenos
    
    for file in os.scandir(nmr_dir): 
        if file.is_file(): 
            file_original = file
            file = file.name.casefold()
            if ('nmr' in file and 
                (file.endswith('.out') or file.endswith('.log'))): 
                
                isom = file.split('_',1)[0]
                
                if isom not in isom_list:continue
                if isom in records.columns : continue # saltea si ya leyo es isomero
    
                # Si llego hasta acá es pq debe analizarse sus vecinos
                
                coord_mat =  extract_coor_matrix (file_original)
                dist_mat = dist_mat_calculator(coord_mat)
                
                C_Br_idx, C_Cl_idx, H_Br_idx, H_Cl_idx = detect_halogen (dist_mat, coord_mat)
                
                temp_wtl = wtl if type(wtl) is not dict else wtl[isom]
                halogen_located = place_halogens_in_wtl(temp_wtl, 
                                                        C_Br_idx, C_Cl_idx, 
                                                        H_Br_idx, H_Cl_idx)
                
                halogen_located.name = isom      
                records = pd.concat([records, halogen_located], axis=1)
                
    # aplastar la matriz de vecinos a halogenos y devolver para acoplar al experimental
    results = records.apply(lambda row: row.dropna().iloc[0] if row.dropna().any() else np.nan, axis=1)
    results.name = 'halogen'
    
    return results
    
                
                
    
    
    