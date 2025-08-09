# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 16:56:19 2023

@author: Franco, Bruno Agustín 

Module capable of detecting inconsistencies in the inputs data.
The filters in this script avoid fatal error in the programme caused by 
the user incorrect usage.
"""

import numpy as np
import pandas as pd
import os, shutil

from collections import Counter
from random import sample

from PyQt5.QtCore import QThread, pyqtSignal


class xlsx_trap(QThread):
    finished = pyqtSignal(str)   

    def __init__(self, file, sheets:list):
        super().__init__()
        self.file = file
        self.sheets = sheets

    def run(self):
        '''Main function that executes the control of the spreadsheets used as 
        "wtl". Adapts the reading engine according to the file format.
        '''
        
        if 'xl' in self.file [-4:]: 
            eng = 'openpyxl'
        if 'od' in self.file [-4:]: 
            eng = 'odf'
        
        xlsx = pd.read_excel(self.file, engine= eng, sheet_name=None)
        
        for sheet in self.sheets : 
        
            if sheet not in xlsx: 
                self.finished.emit(f'¡Input Error!\n"{sheet}" sheet not found\nCorrect the correlation file and try again')
                return
                
            xlsx = xlsx[sheet]
            
            errors = set()
            
            # check columns
            if not all(col in list(xlsx.columns) for col in ['index','nuclei','sp2',
                              'exp_data','exchange','label 1', 'label 2', 'label 3']):  
                self.finished.emit('¡Input Error!\n"Missed column in correlation file\nCorrect it and try again')
                return
                
            # check exp_data
            for i, element in xlsx['exp_data'].items():
                
                try: 
                    element = float (element)
                except: 
                    # print ('ACA2')
                    errors.add ('Not number value in "exp_data" column')
                    continue
                
                if np.isnan(element) : 
                    # print ('ACA3')
                    errors.add ('Miss value in "exp_data" column')
            
            #check nuclei
            if 'nuclei' in xlsx.columns: 
                for i, element in xlsx['nuclei'].items():
                    if element not in ['H','C']:
                        # print ('ACA4')
                        errors.add ('Not C or H in "nuclei" column')
            
            #check diasterotopics 
            for diast, cant in Counter(xlsx['exchange']).most_common():
                
                if type(diast) == float  : 
                    continue
                
                elif cant != 2: 
                    # print (type(diast), diast)
                    # print ('ACA9')
                    errors.add('Uncoupled diasterotopic mark')
                
            #check sp2
            for mark in xlsx['sp2'].unique():
                if mark == 1: continue
            
                if str(mark) not in ['nan','x','X','1']:
                    errors.add('sp2 wrongly identify. Use "x","X" or "1"')
            
            #check labels
            data_df = xlsx.copy()
            for header in ['index','nuclei','sp2','exp_data','exchange']: 
                if header in xlsx.columns : data_df = data_df.drop(columns=[header])
            
            if not 'Missed column' in errors:   
                
                if data_df.shape[1] % 3:
                    # print ('ACA6')
                    errors.add('Incorrect number of "label" columns. Should be multiple of 3')
                    
                if not 'Incorrect number of "label" columns. Should be multiple of 3' in errors: 
                    
                    try : 
                        temp = data_df
                        temp [temp.isna()] = 0
                        np.array(temp, dtype= int)
                        
                        data_df = np.array(data_df, dtype= np.float64)
                        loop = True
                        while loop: 
                            labels_set = data_df[:,:3]
                            labels_set = np.nanmean(labels_set, axis = 1)
                            
                            if any(np.isnan(element) for element in np.nditer(labels_set)): 
                                # print ('ACA8')
                                # print (labels_set)
                                errors.add('Miss value in "label" column')
                                 
                            
                            if data_df.shape[1] == 3: 
                                loop = False 
                                continue 
                            
                            data_df = data_df [:,3:]      
                    
                    except: 
                        # print ('ACA5')
                        errors.add(f'Not interger number in column "label" in sheet {sheet}')
                
            if errors:
                error_message = "¡Input Error!\nThe following errors have been found:\n\n"
                for error in errors:
                    error_message += f"• {error}\n"
                error_message += "\nCalculation can not be done with this file. Correct it and try again."
                
                self.finished.emit(error_message)
                return 
            
            else: 
                self.finished.emit(None)
                return

def isomer_count():
    '''Determine the amount of isomeric candidates to be evaluated
    The files must be named by: isomerID_ * .log 
    '''                
    listing = []
    for file in os.scandir('.'): 
        if file.is_file(): 
            file_original = file
            file = file.name.casefold()
            if ('nmr' in file and 
                (file.endswith('.out') or file.endswith('.log'))): 
                listing.append(file_original.name)
    
    isomer_list = set()
    for file in listing:
        if 'tms' in file.casefold() : 
            isomer_list.add('tms')
            continue
        
        if 'clsp' in file.casefold() : 
            isomer_list.add('clsp')
            continue
        
        if 'brsp' in file.casefold() : 
            isomer_list.add('brsp')
            continue
        
        if file.split('_',1)[0] not in isomer_list:
            isomer_list.add(file.split('_',1)[0])
            
    
    return sorted(isomer_list)


def the_lev_id(funtional, basis_set, solv_mode, key:str, command:str, 
               solvent = None, only_command = False):
    '''It chooses 10% random files and check if the user theory level input
    match the G09 calcs command lines. 
    First assumption is there are no mistakes (wanr is empty). If 
    inconsistencies are found the appropiate warning is added to the list.
    '''
    solvents_list = {'CHCl3': 'Chloroform',
                     'CH2Cl2': 'Dichloromethane',
                     'CCl4': 'CarbonTetraChloride',
                     'H2O': 'Water',
                     'MeOH': 'Methanol',
                     'MeCN': 'Acetonitrile',
                     'DMSO': 'DiMethylSulfoxide',
                     'THF': 'TetraHydroFuran',
                     'Pyridine': 'Pyridine',
                     'Acetone': 'Acetone',
                     'Benzene': 'Benzene' ,
                     'Other':  None}
        
    files = []
    for file in os.scandir('.'): 
        if file.is_file(): 
            file_original = file 
            file = file.name.casefold()
            if (key in file and 
                (file.endswith('.out') or file.endswith('.log'))): 
                files.append(file_original.name)
    
    choose = sample(files, (len(files)//10)+1 )
    warn = set()
    
    for file in choose: 
        
        with open(file, 'r') as file:
            lines = file.readlines()
            
        for i, line in enumerate(lines[75:]):
            if '#' in line: 
                G09command = line
                if not '-----' in lines[i + 76] : G09command += lines[i + 76]
                if command in G09command : break

        if only_command :
            return ['Custom mode. Theory Level not checked'], G09command
        
        if funtional.casefold() not in G09command.casefold(): 
            warn.add(f'{funtional} does not match')
        
        gto, polar = (basis_set).split('(')
        if (gto.casefold() not in G09command.casefold()): 
            warn.add(f'{basis_set} does not match') 
        
        if 'd,p' in polar: 
            if ('d,p' not in G09command.casefold() and
                '**' not in G09command.casefold()): 
                warn.add(f'{basis_set} does not match')
        else: 
            if ('d' not in G09command.casefold() and
                '*' not in G09command.casefold()): 
                warn.add(f'{basis_set} does not match')
            elif ('d,p' in G09command.casefold() or
                '**' in G09command.casefold()): 
                warn.add(f'{basis_set} does not match')
       
        if 'GAS' in solv_mode:
            if 'pcm' in G09command.casefold() or \
               'smd' in G09command.casefold(): 
                warn.add('Not GAS method')
        else: 
            if 'PCM' in solv_mode: 
                if 'smd' in G09command.casefold(): 
                    warn.add('PCM does not match selection')
            else: 
                if 'smd' not in G09command.casefold():
                    warn.add('SMD does not match selection')
                    
        if solvent and solvent != 'Other': 
            if not solvents_list[solvent].casefold() in G09command.casefold():
                warn.add(f'{solvent} solvent does not match')

    if warn : 
        return warn, G09command
    
    else: return None, G09command
                
    
def check_labels_and_isom_cant(xlsx_file, sheet, cant_isom): 
    
    if 'xl' in xlsx_file [-4:]: 
        eng = 'openpyxl'
    if 'od' in xlsx_file [-4:]: 
        eng = 'odf'
    
    data_df = pd.read_excel(xlsx_file, sheet_name=sheet , engine= eng)
    
    for header in ['index','nuclei','sp2','exp_data','exchange']: 
        if header in data_df.columns : data_df = data_df.drop(columns=[header])
    
    if data_df.shape[1]/3 > 1 and data_df.shape[1]/3 != cant_isom:
        return 'Diferent amount of candidates and labels sets\nCorrect the correlation file and try again.'
    
    return None


def exp_data_control(exp_df):
    '''Analyzes for the presence of suspiciously incorrect data.
    It may happen that the user has inadvertently specified some information 
    incorrectly
    '''
    highlights = []
    for cell, (index, row) in enumerate(exp_df.iterrows()):
        
        #cell+2 because in xlsx there is the header and the count starts in 0
        
        if (row['nuclei'] == 'H' and 
            row['exp_data'] > 6 and 
            np.isnan(row['sp2'])):
            highlights.append('C'+str(cell+2))
            
        elif (row['nuclei'] == 'C' and 
              row['exp_data'] > 120 and
              np.isnan(row['sp2'])):
            highlights.append('C'+str(cell+2))
    
        if row['nuclei'] == 'H' and row['exp_data'] > 14:
            highlights.append('B'+str(cell+2))
    
    return highlights


#-----------------------------------------------------------------------------

def sca_e_control(exp, e_matrix):
    '''Analyzes the results of the scaling errors coming from DP4+.
    Because the mathematical formula is applied blindly, this function is 
    appended to help identify gross errors.
    The experimental information and the error matrix must be indicated. As 
    a result, it returns a list of coded locations for printing in 
    spreadsheets with the output_module.py
    '''
    e_matrix = np.abs(e_matrix)
    C = (exp ['nuclei']=='C')
    H = exp['nuclei'].isin(['H','h'])
    
    C_hl = e_matrix > 10
    C_hl[H] = False
    C_hl = np.argwhere((C_hl == True))
    
    H_hl = e_matrix > 0.7
    H_hl[C] = False
    H_hl = np.argwhere((H_hl == True))

    hl = list (C_hl) + list (H_hl)
    highlights = []
    for cell in hl:
        
        col = chr(cell [1] + 6 + 64)
        row = cell [0] + 2
        highlights.append(col+str(row))            
    
    return highlights

# -----------------------------------------------------------------
    
class check_Commmand_Termination_HALO(QThread):
    HALO_answer = pyqtSignal(bool)   
    finished = pyqtSignal(str)   

    def __init__(self, command, key):
        super().__init__()
        self.key = key
        self.command = command
        self.HALO = False 

    def run(self):
        '''Checks that the Gaussian calculations have finished correctly
        Those cases that "Normal Termination" is not found are removed to a 
        subfolder to continue with the calculation of DP4+.
        '''
        removed_files = set()
            
        listing = []
        for file in os.scandir('.'): 
            if file.is_file(): 
                file_original = file
                file = file.name.casefold()
                if (self.key in file and 
                    (file.endswith('.out') or file.endswith('.log'))): 
                    listing.append(file_original.name)
        
        for file in listing:
            size = os.path.getsize(file) / 1024
            if size < 5 : 
                removed_files.add (file)
                continue
            
            with open(file) as f:
                rlines = f.readlines()
            if not any("Normal termination" in line for line in rlines[-5:]):
                removed_files.add (file)
            
            search_HALO = False 
            for line in rlines[84 :]: 
                if not line.strip(): continue
                if 'Symbolic Z-Matrix:' in line :    # comienza a mirar la matriz
                    search_HALO = True 
                    continue 
                if 'Input orientation:' in line : break  # frena la busqueda
                
                if search_HALO: 
                    if ('17' in line.split()[0]) or ('35' in line.split()[0]): 
                        self.HALO = True 
                        break 
                
            
            for i, line in enumerate(rlines[75:]):
                if '#' in line: 
                    commandline = line
                    if not '-----' in rlines[i + 76] : commandline += rlines[i + 76]
                    
                    if self.command in commandline.casefold() : break

            if self.command not in commandline.casefold() : removed_files.add (file)

        if self.HALO: 
            self.HALO_answer.emit(True)
        else: 
            self.HALO_answer.emit(False)
            
        if removed_files:
            dst_folder = 'fail files'
            if not os.path.exists(dst_folder):
                os.makedirs(dst_folder)
                
            for file in removed_files:
                shutil.move(file,dst_folder)         #mueve el .log en Error
            
            display = '''¡ Warning !
    Files have been relocated to the "fail files" directory within the working folder.
    It is strongly advised to rectify any inconsistencies and before run your calculations. 
    Possible errors include: 
        • Unable to locate "Normal Termination"
        • Incorrect command line. "freq" or "nmr"
        
        It is recommended to correct these files before continuing
            '''
            self.finished.emit(display)
        else: 
            self.finished.emit(None)


                
                
                
                
                
                
                
                
                