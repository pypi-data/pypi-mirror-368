# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 11:46:25 2022

@author: Franco, Bruno A.

Auxiliar module by RCC Lab, to procces inputs files of NMR calc and correlate them to
in silico models and experimental data. It has 4 parts: 
        + get_exp_data: from the .xlsx and separate wtl of exp data
        + selections: generates a dictionary of Boolean elements that facilitates
                      matrix operations with specifics elements, like nuclei and error types
        + G09_tens_matix: generates "raw" tensors matrices. It ponderates conformational
                          landscape and keeps G09 order (so it manteins the labels)
        + sort_tens_matrix: correlates "raw" tensor matrix with in silico labels.
                            It also arrange diasterotopic nucleis based on exp data. 
"""
import pandas as pd
import numpy as np
import os, shutil, re

from math import isnan  

def get_exp_data(xlsx, sheet, isom_list=False):
    '''Reads "sheet" of .xlsx file given. 
    Determinates the exp data as a DataFrame and labels as NumpyArrays.
    If isom_list is given, because is used for dp4 calcs, it checks if there
    are different wtl for each candidate. 
    In case, there is only one set of labels the return of "wtl" would be a 
    np.array. 
    If there are several isomers with diferent sets of labels the return of
    "wtl" would be a dict() of np.array for each
    '''
    if 'xl' in xlsx[-4:]: 
        eng = 'openpyxl'
    if 'od' in xlsx[-4:]: 
        eng = 'odf'
    
    data = pd.read_excel(xlsx, sheet_name= sheet ,
                         engine= eng,)
    
    exp_data = data[['index','nuclei','sp2','exp_data','exchange']]
    for index, row in exp_data.iterrows(): 
        if any(x == row['sp2'] for x in ['x','X','1']):
            exp_data.loc[index,'sp2'] = 1
        
    data = data.drop(exp_data.columns,axis=1)
    
    if isom_list:
        
        if data.shape[1] > 3:
            wtl = dict ()
            for isom in isom_list: 
                wtl[isom] = np.array(data.iloc[:,:3])
                if data.shape[1] == 3: 
                    return exp_data, wtl
                data = data.iloc [:,3:]
                
    wtl = np.array(data)
    return exp_data, wtl

#%%
def selections(data):
    '''Classify types of nucleis (subsequently erros and probabilities types) 
    analizing the exp_data information. 
    Returns a pd.DataFrame with boolean columns (True or False) that indicates
    which nuclei of any correlated matrix corresponds to that gruoup'''
    selection = pd.DataFrame(columns=['C','C_sp2','C_sp3',
                                      'H','H_sp2','H_sp3'])
    selection ['C'] = data['nuclei'].isin(['C','c'])
    selection ['C_sp2'] = (data ['nuclei']=='C') & (data ['sp2']==1)
    selection ['C_sp3'] = (data ['nuclei']=='C') & (data ['sp2']!=1)
    
    selection ['H'] = data['nuclei'].isin(['H','h'])
    selection ['H_sp2'] = (data ['nuclei']=='H') & (data ['sp2']==1)
    selection ['H_sp3'] = (data ['nuclei']=='H') & (data ['sp2']!=1)
    
    return selection


#%%
def collect_G09_data(isom_list, nmr_dir, use_energy='', energy_info=''): 
    '''DOC STRINGS
    DOC STRINGS
    DOC STRINGS
    '''
    def get_Gibbs(file, energies):
        'Extract Gibbs energies of every Gaussian 09 output'
        with open (file,'rt') as f:
            lines=f.readlines()
            for i, line in enumerate(reversed(lines)):
                if "thermal Free Energies" in line:
                    Gibbs=float(line.split()[7])
                    if Gibbs in energies:
                        Gibbs += np.random.randint(10,100)/10**10
                    return Gibbs
    
    def get_last_SCF(file, energies):
        with open (file,'rt') as f:
            lines=f.readlines()
            for line in lines[::-1]:     
                if "SCF Done:" in line:
                    energy=float(line.split()[4])
                    return energy        
    
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
    #---------------------------------------------------------------
    
    files = {isom:[] for isom in isom_list}
    
    if energy_info :
        # Si enegy_info es pq tiene el path del directorio energy
        energy_keys = {}
        for file in os.scandir(energy_info): 
            if file.is_file():  
                file_original = file
                file = file.name.casefold()
            
                if ('energy' in file and 
                    (file.endswith('.out') or file.endswith('.log'))):  
                    key = file.replace('energy', "").rsplit(".", 1)[0]
                    energy_keys [key] = file_original.name 
    
    # iterar sobre los archivos nmr  
    for file in os.scandir(nmr_dir): 
        if file.is_file(): 
            file_original = file
            file = file.name.casefold()
            if ('nmr' in file and 
                (file.endswith('.out') or file.endswith('.log'))): 
                
                isom = file.split('_',1)[0]
                
                if isom not in files.keys():continue
                
                # buscar su match si se usan files energy 
                if energy_info :
                    key = file.replace('nmr', "").rsplit(".", 1)[0]
                    if key in energy_keys:
                        files[isom].append( (file_original.name,energy_keys[key]) )
                        del energy_keys [key]
                
                else : 
                    files[isom].append(file_original.name)
    
    # ----------------------------------------------------------------
    isom_tensors = {}
    for isom, isom_files in files.items(): 
        conf_info = {}  # diccionario que almacena la información y luego será un DataFrame
        for file in isom_files: 
            # print (file)
            nmr_file = file if type(file) == str else file[0]
            conf_tens, energy = get_scf_tensors(nmr_file , conf_info.keys())
            conf_info [energy] = conf_tens  
        
            if use_energy == 'gibbs':
                energy_file = os.path.join(energy_info, file[1])
                new_energy = get_Gibbs(energy_file, conf_info.keys())
                conf_info [new_energy] = conf_tens 
                del conf_info [energy]
                
            elif use_energy == 'energy': 
                energy_file = os.path.join(energy_info, file[1])
                new_energy = get_last_SCF(energy_file, conf_info.keys())
                conf_info [new_energy] = conf_tens 
                del conf_info [energy]
        
        isom_tensors[isom] = pd.DataFrame(conf_info)     
    
    return isom_tensors

def Boltzman_pond (tens_by_conf) : 
    '''DOC STRING
    DOC STRING
    '''
    energies = tens_by_conf.columns
    energies = np.array(energies)*627.5095 #units change to kcal/mol 
    ground = energies.min()
    relativ_e = energies - ground             #relative energies
    # P_Boltz = np.exp(-relativ_e*4.18/2.5)      #Boltzmann prob calc at 25°C
    P_Boltz = np.exp(-relativ_e/(0.0019872*298.15))      
    contributions = P_Boltz / P_Boltz.sum()  #normalization   
    pond_tens = np.average(tens_by_conf, weights=contributions, axis=1)
    return pond_tens



#%%
def sort_tens_matrix(G09_tens_matrix, isomer_list, exp_data, wtl):
    '''Sort the raw tensor matrix order by the G09 labels following the 
    correlation labels informed by user. To sort and mean each isomer nucleis
    it uses the auxiliar funtion: sort_by_tens(G09_tens_list, isom_labels). 
    Returns a np.array() with tensor matrix correlated with the labels from
    input (rows: nucleus, columns: isom candidates)
    To finish, the diasterotopic nucleis are rearrange acoding to the exp_data'''
    sorted_tens_matrix= np.empty((exp_data.shape[0],len(isomer_list)))
    
    for i, isom in enumerate(isomer_list):
        
        isom_wtl = wtl[isom] if type(wtl) is dict else wtl
        G09_tens_list = G09_tens_matrix[:,i]
         
        isom_sorted_matrix= np.empty((isom_wtl.shape[0],3))
        isom_sorted_matrix[:] = np.nan
        
        unmatch_labels = []
        for y in range (isom_wtl.shape[0]):
            for x in range (3):
                if not isnan(isom_wtl[y,x]):
                    index = int(isom_wtl[y,x])
                    try : 
                        isom_sorted_matrix[y,x] = G09_tens_list[index-1] 
                        #-1 because G09 counts from 1 and Python from 0
                    except: 
                        unmatch_labels.append (index)
                        
        if unmatch_labels : return str(unmatch_labels)
        
        isom_tens = np.nanmean(isom_sorted_matrix, axis = 1)
        sorted_tens_matrix[:,i] = diasterotopic(isom_tens, exp_data)
    
    return sorted_tens_matrix


def diasterotopic(tens_vector, exp_data):
    '''Rearranges the nuclei identified as diasterotopic, making the 
    largest experimental shift correspond to that calculated.
    For them, each pair of diasterotopic nuclei must be identified in the 
    exchange column with a letter.
    Returns a vector with the diasterotopics nucleis rearranged. 
    '''
    for diast in exp_data['exchange'].unique(): 
        #saltea los q no son diasterotopicos
        if (type(diast) == np.float64 or type(diast) == float) and isnan(diast): continue
        
        #se obtienen los indices de los nucleos diast
        nucleos = exp_data.loc[exp_data['exchange'] == diast].index.tolist()
        #for i,j in enumerate(nucleos):
        #    nucleos[i] = exp_data.index.get_loc(j)
            
        #se realiza un back up de los tensores 
        tensors = tens_vector[exp_data['exchange'] == diast]
        
        #los ordena de manera opuesta ya q el tensor es inversamente 
        #proporcional al desplazamiento
        max_d = max(exp_data.loc[exp_data['exchange'] == diast,'exp_data'])
        if exp_data.iloc[nucleos[0]]['exp_data'] == max_d:
             tens_vector[nucleos[0]] = min(tensors)
             tens_vector[nucleos[1]] = max(tensors)
        else:
            tens_vector[nucleos[0]] = max(tensors)
            tens_vector[nucleos[1]] = min(tensors)
            
    return tens_vector

# funciones agregadas a DP4+App_v2 -----------------------------------------
def cut_links(directory) : 
    '''DOC STRINGS
    DOC STRINGS
    DOC STRINGS
    '''
    
    def split_gaussian_link_file(file_path):
        '''DOC STRING
        DOC STRING
        DOC STRING
        '''
        
        # Lectura del archivo
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Patrón regex para detectar las secciones que terminan con "Normal termination"
        pattern = r"(.*?Normal termination.*?(?:\n|$))"
        
        # División del contenido basado en el patrón
        calculations = re.findall(pattern, content, re.DOTALL)
        
        if len (calculations) != 2 : 
            dst_folder = os.path.join(os.path.dirname(file_path),'fail files')
            if not os.path.exists(dst_folder): os.mkdir(dst_folder)
            shutil.move (file_path, os.path.join(dst_folder,file_path))
            return True
        
        for calculation in calculations:
            
            lines = calculation.splitlines()
            for i, line in enumerate(lines[75:]):
                if '#' in line: 
                    command_line = line
                    if not '-----' in lines[i + 76] : command_line += lines[i + 76]
                    break
                        
            folder = os.path.dirname(file_path)
            file, extention = os.path.basename(file_path).split('.')
            file = file.replace('nmr','')
            file = file.replace('energy','')
            file = file.replace('freq','')
            
            if 'nmr' in command_line: 
                output_file = os.path.join(folder,'nmr calcs', f'{file}_nmr.{extention}')
            else: 
                output_file = os.path.join(folder,'energy calcs', f'{file}_energy.{extention}')
            
            with open(output_file, 'w') as file:
                file.write(calculation)
        return False
    # --------------------------------------------------------------------
    fail_sign = False
    fail_files = False
    os.chdir(directory)
    if not os.path.exists('nmr calcs'): os.mkdir('nmr calcs')
    if not os.path.exists('energy calcs'): os.mkdir('energy calcs')
    
    for file in os.scandir(directory): 
        if file.is_file():  
            file_original = file
            file = file.name.casefold()
        
            if ('nmr' in file and 
                (file.endswith('.out') or file.endswith('.log'))):  
                
                fail_files = split_gaussian_link_file(file_original.name) 
            
            if fail_files : fail_sign = True
                
    return os.path.join(os.path.join(directory,'nmr calcs')), \
           os.path.join(os.path.join(directory,'energy calcs')), \
           fail_sign
           
           
def match_nmr_energy(nmr_dir, energy_dir, check_gibbs):
    
    def check_freq_command(filepath):
        with open(filepath, 'r') as file:
            lines = file.readlines()
            for i, line in enumerate(lines[75:]):
                if '#' in line: 
                    command_line = line
                    if not '-----' in lines[i + 76] : command_line += lines[i + 76]
                    break
            
            if 'freq' in command_line.casefold(): return True
            
            else : return False
    
    # generar una lista con los key de los archivos energy
    all_energy_count = 0
    energy_keys = {}
    for file in os.scandir(energy_dir): 
        if file.is_file():  
            file_original = file
            file = file.name.casefold()
        
            if ('energy' in file and 
                (file.endswith('.out') or file.endswith('.log'))): 
                
                if check_gibbs : 
                    if not check_freq_command(os.path.join(energy_dir,file_original.name)) : continue
                
                key = file.replace('energy', "").rsplit(".", 1)[0]
                all_energy_count += 1
                energy_keys [key] = file_original.name 
    
    # iterar sobre los archivos nmr y buscar su match 
    all_nmr_count = 0
    nmr_missmatched = []
    for file in os.scandir(nmr_dir): 
        if file.is_file(): 
            file_original = file
            file = file.name.casefold()
            if ('nmr' in file and 
                (file.endswith('.out') or file.endswith('.log'))): 
                
                all_nmr_count += 1
                key = file.replace('nmr', "").rsplit(".", 1)[0]
                if key in energy_keys:
                    del energy_keys [key]
                else:     
                    nmr_missmatched.append (file_original.name)
        
    if all_energy_count-len(energy_keys) == 0 or all_nmr_count - len(nmr_missmatched)== 0: 
        return 'Stop calc'
        
    for file in nmr_missmatched : 
        dst_folder = os.path.join(nmr_dir,'excluded nmr files')
        if not os.path.exists(dst_folder): os.mkdir(dst_folder)
        shutil.move (os.path.join(nmr_dir,file), os.path.join(dst_folder,file))
        
    for _,file in energy_keys.items(): 
        dst_folder = os.path.join(energy_dir,'excluded energy files')
        if not os.path.exists(dst_folder): os.mkdir(dst_folder)
        shutil.move (os.path.join(energy_dir,file), os.path.join(dst_folder,file))

    if nmr_missmatched or energy_keys : 
        return True
    else : 
        return False