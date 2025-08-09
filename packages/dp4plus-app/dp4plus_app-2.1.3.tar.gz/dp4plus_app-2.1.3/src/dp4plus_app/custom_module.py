# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 13:23:46 2023

@author: Franco, Bruno Agustín 
         
DP4+ parameterization module
It uses the DP4+ nmr correlation and calculation modules, as well as having 
its own functions to complete the proccess. 
"""

from PyQt5.QtCore import QThread, pyqtSignal


import pandas as pd
import numpy as np
import scipy.stats as st
import os

##### AGREGAR RELATIVE IMPORTS 
from . import correlation_module as nmr_correl
from . import dp4_module as dp4
from . import bugs_a_warning_module as warn
from . import output_module as output

def add_errors(e_vectors, df_selections, uns_e, sca_e):
    '''Attaches the errors of a molecule to the global parameterization sets
    '''
    e_vectors['Csca'] = np.append(e_vectors['Csca'], sca_e[df_selections['C']])
    e_vectors['Hsca'] = np.append(e_vectors['Hsca'], sca_e[df_selections['H']])
    
    e_vectors['Csp2'] = np.append(e_vectors['Csp2'], uns_e[df_selections['C_sp2']])
    e_vectors['Csp3'] = np.append(e_vectors['Csp3'], uns_e[df_selections['C_sp3']])
    
    e_vectors['Hsp2'] = np.append(e_vectors['Hsp2'], uns_e[df_selections['H_sp2']])
    e_vectors['Hsp3'] = np.append(e_vectors['Hsp3'], uns_e[df_selections['H_sp3']])
    
    return e_vectors

def get_parameters(e_vectors):
    '''Estimates the parameters of the t studen probability distribution
    '''
    # out_file = os.path.normpath(os.path.expanduser("~/Desktop"))
    # out_file = os.path.join(out_file,'Qt_temp_Train.xlsx')
    # with pd.ExcelWriter(out_file) as writer:     
    #     for label,data in e_vectors.items(): 
    #         temp = pd.DataFrame(data)
    #         temp.to_excel(writer, sheet_name=label)
    
    param = pd.DataFrame(columns=['n', 'm', 's'],
                         index = ['Csp3','Csp2','Csca',
                                  'Hsp3','Hsp2','Hsca'])
    
    param.loc['Csca'] = st.t.fit(e_vectors['Csca'])
    param.loc['Hsca'] = st.t.fit(e_vectors['Hsca'])
    
    param.loc['Csp2'] = st.t.fit(e_vectors['Csp2'])
    # print (len (e_vectors['Csp3']))
    # print (st.t.fit(e_vectors['Csp3']))
    param.loc['Csp3'] = st.t.fit(e_vectors['Csp3'])
    
    param.loc['Hsp2'] = st.t.fit(e_vectors['Hsp2'])
    param.loc['Hsp3'] = st.t.fit(e_vectors['Hsp3']) 
    
    param.loc['Csca','m'] = 0.0
    param.loc['Hsca','m'] = 0.0
    
    return param

class train_Thread(QThread):
    '''DOC STRING
    DOC STRING
    DOC STRING
    '''  
    results = pyqtSignal(pd.DataFrame, dict, bool, dict)
    finished = pyqtSignal(dict)
    message = pyqtSignal(str)  
    correlation_warn = pyqtSignal(str)
    
    def __init__(self, thelev_name, dirname, xlsname, molecules:list):
        super().__init__()
        
        self.thelev_name = thelev_name
        self.dirname = dirname
        self.xlsname = xlsname
        self.molecules = molecules
        
    
    def run(self):
        warn_flag = False
        small_sample = False
            
        # Start calculation -------------------------------------------------
        os.chdir(self.dirname)
        self.message.emit("Starting training ")
        
        # determinar TMS
        tms_tens = nmr_correl.collect_G09_data(['tms'], self.dirname ) 
        tms_tens = tms_tens['tms'].iloc[:,0]        
        tms_tens = pd.Series(tms_tens)
        tms_tens = tms_tens.groupby(tms_tens).mean()
        
        tms_tens = {'H': tms_tens.iloc[(tms_tens - 30).abs().argmin()],
                    'C': tms_tens.iloc[(tms_tens - 190).abs().argmin()] }
        
        # determinar HALO 
        HALO_tens = get_MSTD('clsp2', self.dirname)
        
        # Recolectar errores 
        e_vectors = {'Csca':np.empty(0), 'Csp2':np.empty(0), 'Csp3':np.empty(0),
                    'Hsca':np.empty(0), 'Hsp2':np.empty(0), 'Hsp3':np.empty(0)}
        
        for molec in self.molecules:
            # saltea los estandares 
            if any(key in molec.casefold() for key in ['tms','clsp','brsp' ]) : continue
        
        
            exp_data, wtl = nmr_correl.get_exp_data(self.xlsname, molec)
            df_selections = nmr_correl.selections(exp_data)
            
            tens_by_conf_a_molec = nmr_correl.collect_G09_data([molec], self.dirname)
            tens_by_molec = nmr_correl.Boltzman_pond (tens_by_conf_a_molec[molec])
            tens_by_molec = tens_by_molec[:,np.newaxis]
            tens_by_molec_sorted = nmr_correl.sort_tens_matrix(tens_by_molec, [molec], exp_data, wtl) 
            if type(tens_by_molec_sorted) == str : 
                self.finished.emit({'statusBar': u"Calculation aborted \u2717",
                                    'popupTitle': u'Calculation aborted \u2717', 
                                    'popupText': f'''Attention:
    The calculation was aborted because in molecule: {molec} labels: {tens_by_molec_sorted} could not be matched with its corresponding nucleus. 
    Please correct the correlation file and try again.'''})
                return 
            
            uns = dp4.get_uns_shifts(tens_by_molec_sorted,df_selections, tms_tens )
            sca = dp4.get_sca_shifts(uns, df_selections, exp_data)
            
            uns_e = dp4.calc_errors(uns,exp_data)
            sca_e = dp4.calc_errors(sca,exp_data)
            
            e_hl = warn.sca_e_control(exp_data, sca_e)
            exp_hl = warn.exp_data_control(exp_data)
            if e_hl + exp_hl: 
                  output.add_highlights_warn(self.xlsname, molec, 
                                            e_hl, exp_hl)
                  warn_flag = True
            
            e_vectors = add_errors(e_vectors, df_selections, uns_e, sca_e)
            
        self.param  = get_parameters(e_vectors)
        if any (len(vector)<150 for e_type,vector in e_vectors.items()): 
            small_sample = True 
        
        self.message.emit("Finishing training ")
        
        if warn_flag :
            self.correlation_warn.emit('''Attention:
Some possiible errors were found in the correlation spread sheet
Check the highlights in {e_hl + exp_hl}
It is recommended to correct the inconsistency''')

        self.finished.emit({})

        self.results.emit (self.param , tms_tens, small_sample, HALO_tens )
        # DEVOLVER LOS PARAMETROS, EL STANDARD Y SI HAY Q CAMBIAR LOS NHU

            
    
def get_MSTD (key, nmr_dir) : 
    '''
    '''    
    # -------------------------------------------------------------------------
    def extract_coor_matrix (file): 
        with open (file,'rt') as f:
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
    
    def get_scf_tensors(file, energies):
        '''Reads G09 calculus in the working folder. Sistematicaly stracts the 
        isotropic shielding tensors and SCF energies.
        Returns a np.array of tensors and energy as a float 
        It also corrects repeted energies (SHOULD CHECK THEY ARE NOT DUPLICATES)
        '''
        
        tensors=[]
        with open (file,'rt') as f:
            lines=f.readlines()
            for line in lines:     
                if "SCF Done:" in line:
                    energy=float(line.split()[4])
                    
                    if energy in energies:
                        energy += np.random.randint(10,100)/10**10
                    
                if "Isotropic = " in line:
                    tensors.append(float(line.split()[4]))
                    
                if 'Population analysis using the SCF density' in line and tensors : break 
                    
        return np.array(tensors), energy  
    
    # Main Funtion --------------------------------------------------------
    MSTD_files = {'Cl_sp2' : '',   
                  'Cl_sp3' : '',
                  'Br_sp2' : '',
                  'Br_sp3' : '',}
    
    # iterar sobre los archivos nmr  
    for file in os.scandir(nmr_dir): 
        
        if not file.is_file(): continue
        
    
        file_original = file
        file = file.name.casefold()
        
        # Filtros 
        if not 'nmr' in file : continue
        if not file.endswith('.out') and not file.endswith('.log'): continue
        
        # Encontrar archivo / os
        if 'clsp2' in file :   MSTD_files['Cl_sp2'] = file_original
        if 'clsp3' in file :   MSTD_files['Cl_sp3'] = file_original
        if 'brsp2' in file :   MSTD_files['Br_sp2'] = file_original
        if 'brsp3' in file :   MSTD_files['Br_sp3'] = file_original  
        
        
    MSTD = {'Cl_sp2' : [0,0],   # [C, H] en ese orden
            'Cl_sp3' : [0,0],
            'Br_sp2' : [0,0],
            'Br_sp3' : [0,0],}
    
    for key, file in MSTD_files.items():
        if not file : continue
        
        coord_mat =  extract_coor_matrix (file)
        dist_mat = dist_mat_calculator(coord_mat)
        C_Br_idx, C_Cl_idx, H_Br_idx, H_Cl_idx = detect_halogen (dist_mat, coord_mat)
    
        tens, _ = get_scf_tensors( file, []) 
        
        if C_Cl_idx and H_Cl_idx:   MSTD[key] = [np.mean([tens[idx-1] for idx in C_Cl_idx]), 
                                                 np.mean([tens[idx-1] for idx in H_Cl_idx])]
        
        if C_Br_idx and H_Br_idx:   MSTD[key] = [np.mean([tens[idx-1] for idx in C_Br_idx]), 
                                                 np.mean([tens[idx-1] for idx in H_Br_idx])]
        
    return MSTD
    
    
    
    
    
            
