# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 11:42:07 2024

@author: Franco, Bruno Agustín 

AGREGAR DOCUMENTACION
"""
import os
from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd

#AGREGAR RELATIVE PATH PARA QUE ANDE EN PYPI
from . import correlation_module as nmr_correl
from . import output_module as output
from . import dp4_module as dp4
from . bugs_a_warning_module import the_lev_id
from . HALO_module import HALO_calc

class gibbs_dp4_Thread(QThread):
    '''DOC STRING
    DOC STRING
    DOC STRING
    '''    
    finished = pyqtSignal(dict)
    message = pyqtSignal(str)  
    
    def __init__(self, mode, dirname, isoms_list, xlsname, the_lev, solvent, \
                 solv_tens, energy, energy_info, nmr_command, the_lev_warns):
        super().__init__()
        
        self.mode = mode
        
        data_base = os.path.join(os.path.dirname(__file__), "data_base_QM.xlsx")
        self.parameters = pd.read_excel(data_base,sheet_name=the_lev,index_col=0)
        
        self.working_folder = dirname
        self.dirname = dirname
        self.isoms_list = isoms_list
        self.xlsname = xlsname
        self.the_lev = the_lev
        self.the_lev_warns = the_lev_warns
        self.nmr_command = nmr_command
        
        self.solvent = solvent
        if solv_tens and solvent == 'Other': 
            self.standard = solv_tens
        else : 
            if not solvent:
                self.standard = pd.read_excel(data_base, sheet_name='GAS', index_col=0)
            else : 
                self.standard = pd.read_excel(data_base, sheet_name=solvent, index_col=0)
        
            self.standard = self.standard.loc[the_lev]
        
        self.energy = energy
        self.energy_info = energy_info
    
    def run(self):
        
        match_warn, split_warn = False, False
        check_gibbs = False
        if self.energy_info == 'link' : 
            self.message.emit("Splitting Gaussian link files ")
            self.dirname, self.energy_info, split_warn = nmr_correl.cut_links (self.dirname)
            check_gibbs = True if self.energy == 'gibbs' else False
        
        if self.energy_info: 
            self.message.emit('Cheking energy files')
            match_warn = nmr_correl.match_nmr_energy(self.dirname, self.energy_info, 
                                                     check_gibbs)
            
            if match_warn == 'Stop calc': 
                self.finished.emit({'statusBar': u"Calculation aborted \u2717",
                                    'popupTitle': u'Calculation aborted \u2717', 
                                    'popupText': '''Attention:
The calculation was aborted, here are possible causes:
    . The link is broken 
    . Files could not be paired 
    . If Gibbs was required, freq command was not found
Please correct your files and try again.'''})
                return 
            
        # Start calculation -------------------------------------------------
        os.chdir(self.dirname)
        self.message.emit("Starting calculations ")
        
        if self.mode == 'QM': 
            result = dp4.calc( self.isoms_list, self.dirname, self.xlsname, 
                          self.energy, self.energy_info, 
                          self.standard, self.parameters)
            
        elif self.mode == 'HALO': 
            MSTD_stand = os.path.join(os.path.dirname(__file__), 'MSTD-QM-Stand.xlsx')
            MSTD_stand = pd.read_excel(MSTD_stand, index_col=0)
            MSTD_stand = MSTD_stand.loc[[self.the_lev, 'EXP']].T
            
            result = HALO_calc( self.isoms_list, self.dirname, self.xlsname, 
                          self.energy, self.energy_info, 
                          self.standard, self.parameters, MSTD_stand)
            
            # modificacion para impimir en excel 
            MSTD_stand.loc['C',:] = [self.standard['C'], None]
            MSTD_stand.loc['H',:] = [self.standard['H'], None]
            self.standard = MSTD_stand    
        
        if type(result) == str:
            self.finished.emit({'statusBar': u"Calculation aborted \u2717",
                                    'popupTitle': u'Calculation aborted \u2717', 
                                    'popupText': f'''Attention:
The calculation was aborted because labels: {result} could not be matched with its corresponding nucleus. 
Please correct the correlation file and try again.'''})
            return 

        self.message.emit("Generating output ")
        
        if self.energy_info: 
            os.chdir(self.energy_info)
            _, energy_command = the_lev_id('', '', '', 'energy', '', only_command=True)
            energy_command = energy_command + f" - ({self.energy if self.energy == 'gibbs' else 'SCF'})"
        else: 
            energy_command = self.nmr_command +' - (SCF)'
        
        output.gen_out_dp4(self.working_folder,
                           self.mode, 
                            self.isoms_list,
                            self.solvent, 
                            self.standard,
                            self.the_lev,
                            self.the_lev_warns,
                            self.nmr_command ,                           
                            self.parameters, 
                            result,
                            energy_command = energy_command)
        
        # pasar la señal 
        if match_warn or split_warn: 
            self.finished.emit({'statusBar': u"Calculation finished with warnings \u2713",
                                'popupTitle': u'Calculation successfully completed \u2713', 
                                'popupText': 'Attention:\nSome NMR and/or energy calculations were identified as corrupted or mismatched and have been moved to the corresponding "fail" folders for further inspection.\nThese files may not have been included in the final results.'})
        else: 
            self.finished.emit({'statusBar': u"Calculation finished successfully \u2713",
                            'popupTitle': u'Proccess completed \u2713', 
                            'popupText': 'Find the results in your working folder'})
        
        return
    
class simple_dp4_Thread(QThread):
    '''DOC STRING
    DOC STRING
    DOC STRING
    '''    
    finished = pyqtSignal(dict)
    message = pyqtSignal(str)  
    
    def __init__(self, mode, dirname, isoms_list, xlsname, the_lev, solvent, \
                 solv_tens, nmr_command, the_lev_warns):
        
        '''mode: es una cadena que sea MM , HALO-MM o Custom'''
        
        super().__init__()
        
        self.mode = mode 
        
        if 'MM' in mode : 
            data_base = "data_base_MM.xlsx" 
        elif 'Custom' in mode : 
            data_base = "data_base_Custom.xlsx"
        
        data_base = os.path.join(os.path.dirname(__file__), data_base)
        self.parameters = pd.read_excel(data_base,sheet_name=the_lev,index_col=0)
        
        self.working_folder = dirname
        self.dirname = dirname
        self.isoms_list = isoms_list
        self.xlsname = xlsname
        self.the_lev = the_lev
        self.the_lev_warns = the_lev_warns
        self.nmr_command = nmr_command
        
        # definición del solvente 
        if 'MM' in mode:       
            self.solvent = solvent
            if solv_tens and solvent == 'Other': 
                self.standard = solv_tens
            else : 
                if not solvent:
                    self.standard = pd.read_excel(data_base, sheet_name='GAS', index_col=0)
                else : 
                    self.standard = pd.read_excel(data_base, sheet_name=solvent, index_col=0)
            
                self.standard = self.standard.loc[the_lev]
                
        elif 'Custom' in mode : 
            self.solvent = ''             # el solvente no está definido pq es nivel custom 
            self.standard = pd.read_excel(data_base, sheet_name='standard', index_col=0)
            self.standard = self.standard.loc[the_lev]
        
        # self.energy = energy
        # self.energy_info = energy_info
    
    def run(self):
        # Start calculation -------------------------------------------------
        os.chdir(self.dirname)
        self.message.emit("Starting calculations ")
        
        if 'HALO' in self.mode: 
            if 'Custom' in self.mode: 
                MSTD_stand = os.path.join(os.path.dirname(__file__), 'MSTD-Custom-Stand.xlsx')
            else : 
                MSTD_stand = os.path.join(os.path.dirname(__file__), 'MSTD-MM-Stand.xlsx')
            
            MSTD_stand = pd.read_excel(MSTD_stand, index_col=0)
            MSTD_stand = MSTD_stand.loc[[self.the_lev, 'EXP']].T
            
            result = HALO_calc( self.isoms_list, self.dirname, self.xlsname, 
                          'nmr', '', self.standard, self.parameters, MSTD_stand)
            
            # modificacion para impimir en excel 
            MSTD_stand.loc['C',:] = [self.standard['C'], None]
            MSTD_stand.loc['H',:] = [self.standard['H'], None]
            self.standard = MSTD_stand   
            
        else: 
            result = dp4.calc( self.isoms_list, self.dirname, self.xlsname, 
                          'nmr', '', self.standard, self.parameters)
        
        if type(result) == str:
            self.finished.emit({'statusBar': u"Calculation aborted \u2717",
                                    'popupTitle': u'Calculation aborted \u2717', 
                                    'popupText': f'''Attention:
The calculation was aborted because labels: {result} could not be matched with its corresponding nucleus. 
Please correct the correlation file and try again.'''})
            return 

        self.message.emit("Generating output ")
        output.gen_out_dp4(self.working_folder,
                           self.mode, 
                            self.isoms_list,
                            self.solvent, 
                            self.standard,
                            self.the_lev,
                            self.the_lev_warns,
                            self.nmr_command ,                           
                            self.parameters, 
                            result )
        

        self.finished.emit({'statusBar': u"Calculation finished successfully \u2713",
                        'popupTitle': u'Proccess completed \u2713', 
                        'popupText': 'Find the results in your working folder'})
        
        return    
    