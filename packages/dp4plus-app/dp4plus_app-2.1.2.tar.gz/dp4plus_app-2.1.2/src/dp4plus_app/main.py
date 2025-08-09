# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 14:04:50 2024

@author: Franco, Bruno Agustín 

AGREGAR DOCUMENTACION
"""


from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, \
                            QFileDialog, QRadioButton, QComboBox, QTabWidget, \
                            QDoubleSpinBox, QMessageBox, QDialog, QCheckBox, \
                            QDialogButtonBox, QWidget, QLineEdit

from PyQt5 import uic
from PyQt5.QtCore import QTimer, QEventLoop, pyqtSignal, QThread

from random import randint
import pandas as pd

import sys, subprocess, os, shutil, time

sys.path.append(os.path.dirname(__file__))

from . Qt_threads import gibbs_dp4_Thread, simple_dp4_Thread
from . output_module import gen_out_custom, save_MSTD_HALO
from . import bugs_a_warning_module as trap
from . custom_module import train_Thread

class UI(QMainWindow): 
    '''Clase principal de la User Interface (UI). Contempla el espacio de los tabs, 
    el botón de salida y la barra de estado. 
    Además hay alguna funciones auxiliares de ventanas emergentes para interactuar o 
    informar. Se incluye tambien la animación del StatusBar para dar claridad del uso
    Cada programa (DP4+, MM-DP4+ y Custom) funcionan de forma independiente en 
    tabs (widgets) separados. 
    '''    
    def __init__(self): 
        super (UI, self).__init__()
        
        #load the ui file
        
        GUI = os.path.join(os.path.dirname(__file__),'GUI2','GUI.ui' )
        uic.loadUi(GUI, self)
        self.setWindowTitle('DP4+ App')
        
        self.exit = self.findChild(QPushButton,'exit')
        self.exit.clicked.connect(self.quit_application)
        
        self.statusBar.showMessage('Welcome to DP4+ App')
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.status_bar_progress_animation)
        self.statusBar_loading = ''
        self.dots = 0
        
        self.MainTab = self.findChild(QTabWidget, 'tabWidget')
        self.MainTab.currentChanged.connect(self.Tab_changed)
        
        # dp4plus_tab
        self.dp4_tab = dp4_tab()                        # Crear instancias de las pestañas
        self.MainTab.insertTab(0,self.dp4_tab, "DP4+")  # Añadir las pestañas al QTabWidget
        self.dp4_tab.update_status.connect(self.update_statusBar) # Conectar señales
        self.dp4_tab.info_pp.connect(self.informative_PopUp)
        self.dp4_tab.timer.connect(self.timer_switch)
        self.tabWidget.setCurrentIndex(0)
        
        # mm_dp4plus_tab
        self.mm_dp4_tab = mm_dp4_tab()                        # Crear instancias de las pestañas
        self.MainTab.insertTab(1,self.mm_dp4_tab, "MM-DP4+")  # Añadir las pestañas al QTabWidget
        self.mm_dp4_tab.update_status.connect(self.update_statusBar) # Conectar señales
        self.mm_dp4_tab.info_pp.connect(self.informative_PopUp)
        self.mm_dp4_tab.timer.connect(self.timer_switch)
        
        # custom_tab
        self.custom_tab = custom_dp4_tab()                        # Crear instancias de las pestañas
        self.MainTab.insertTab(2,self.custom_tab, "Custom")  # Añadir las pestañas al QTabWidget
        self.custom_tab.update_status.connect(self.update_statusBar) # Conectar señales
        self.custom_tab.info_pp.connect(self.informative_PopUp)
        self.custom_tab.timer.connect(self.timer_switch)
        
    # Controling funtions ---------------------------------------------------
    def Tab_changed(self, index):
        self.statusBar.clearMessage()       # Clear the status bar when the tab is changed
    
    def quit_application(self):
        self.close()

    def status_bar_progress_animation(self):
        self.dots = (self.dots + 1) % 4
        self.statusBar.showMessage(self.statusBar_loading + ' .' * self.dots)
        
    def update_statusBar(self, message): 
        self.statusBar_loading = message
        self.statusBar.showMessage(message)
        
    def timer_switch(self, ON): 
        if ON : 
            self.timer.start(500)
        else : 
            self.timer.stop()
        
    def informative_PopUp(self, Icon, Text, InformativeText):
        self.timer.stop()
        
        if not Text : return 
        
        msg_box = QMessageBox()
        msg_box.setIcon(Icon)
        msg_box.setWindowTitle("DP4+App Status")
        msg_box.setText(Text)
        msg_box.setInformativeText(InformativeText) #control
        msg_box.exec_()
    
# -----------------------------------------------------------------------------
# Auxiliar dialogs y pop up -------------------------------------------------
        
def show_custom_message(icon, title, text, yes='Continue', no='Cancel'):
    '''Genera una dialogo emergente con 2 botones.
    Puede ser llamada de cualquier tab
    '''
    msg_box = QMessageBox()
    msg_box.setIcon(icon)
    msg_box.setWindowTitle('DP4+ App')
    msg_box.setText(title)
    msg_box.setInformativeText(text)
    msg_box.setStandardButtons(QMessageBox.No | QMessageBox.Yes )
    msg_box.button(QMessageBox.Yes).setText(yes)
    msg_box.button(QMessageBox.No).setText(no)
    
    result = msg_box.exec_()
    
    return result == QMessageBox.Yes        

def SolventTensorsDialog():
    '''Genera dialogo para ingresar un los valores del tensor C y H de un solvente
    que se desee. Toma solo valores tipo float. 
    '''
    # Cargar el diseño del diálogo desde el archivo .ui
    Dialog = os.path.join(os.path.dirname(__file__), 'GUI2', 'solvent_dialog.ui')
    dialog = QDialog()
    uic.loadUi(Dialog, dialog)
    dialog.setWindowTitle('DP4+ App')

    # Obtener los widgets definidos en el archivo .ui
    tensorC_input = dialog.findChild(QDoubleSpinBox, 'tensorC_input')
    tensorH_input = dialog.findChild(QDoubleSpinBox, 'tensorH_input')

    # Conectar los botones
    buttons = dialog.findChild(QDialogButtonBox, 'buttonBox')
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)

    # Ejecutar el diálogo y obtener el resultado
    answer = dialog.exec_()
    tensorC = tensorC_input.value()
    tensorH = tensorH_input.value()

    return answer, tensorC, tensorH    

class DownloadThread(QThread):  
    '''Hilo para copiar/descargar las carpetas de ejemplo sin usa el hilo de la 
    interfaz grafica. 
    '''
    finished_signal = pyqtSignal(str)
    fail_signal = pyqtSignal(str)
    
    def __init__(self, src_folder, desktop):
        super(DownloadThread, self).__init__()
        self.src_folder = src_folder
        self.desktop = desktop
        
    def run(self):
        folder_name = os.path.basename(self.src_folder)
        dst_folder = os.path.join(self.desktop, folder_name)
        if os.path.exists(dst_folder):
            dst_folder = dst_folder + f'_{str(randint(0, 100))}'
            
        try: 
            shutil.copytree(self.src_folder, dst_folder)
            self.finished_signal.emit(dst_folder)
        except Exception as e :
            # print (e)
            self.fail_signal.emit(dst_folder)
        
# -----------------------------------------------------------------------------
class HALO_stand_popup(QDialog):
    '''
    '''
    def __init__(self, HALO_Stand):
        super().__init__()

        # Load the .ui file
        ui_path = os.path.join(os.path.dirname(__file__), 'GUI2', 'HALO_Standard.ui')
        uic.loadUi(ui_path, self)
        self.setWindowTitle('DP4+ App')

        self.HALOStand = HALO_Stand

        # Find widgets
        self.C_Cl_sp2 = self.findChild(QDoubleSpinBox, 'C_Cl_sp2')
        self.C_Cl_sp2.setValue(self.HALOStand['Cl_sp2'][0])
        self.H_Cl_sp2 = self.findChild(QDoubleSpinBox, 'H_Cl_sp2')
        self.H_Cl_sp2.setValue(self.HALOStand['Cl_sp2'][1])
        self.C_Cl_sp3 = self.findChild(QDoubleSpinBox, 'C_Cl_sp3')
        self.C_Cl_sp3.setValue(self.HALOStand['Cl_sp3'][0])
        self.H_Cl_sp3 = self.findChild(QDoubleSpinBox, 'H_Cl_sp3')
        self.H_Cl_sp3.setValue(self.HALOStand['Cl_sp3'][1])
        
        self.C_Br_sp2 = self.findChild(QDoubleSpinBox, 'C_Br_sp2')
        self.C_Br_sp2.setValue(self.HALOStand['Br_sp2'][0])
        self.H_Br_sp2 = self.findChild(QDoubleSpinBox, 'H_Br_sp2')
        self.H_Br_sp2.setValue(self.HALOStand['Br_sp2'][1])
        self.C_Br_sp3 = self.findChild(QDoubleSpinBox, 'C_Br_sp3')
        self.C_Br_sp3.setValue(self.HALOStand['Br_sp3'][0])
        self.H_Br_sp3 = self.findChild(QDoubleSpinBox, 'H_Br_sp3')
        self.H_Br_sp3.setValue(self.HALOStand['Br_sp3'][1])
        
        
        self.save_btn = self.findChild(QPushButton, 'Save_btn')
        
        # connect funtions 
        self.save_btn.clicked.connect(self.save_a_close)
        
    def save_a_close (self) : 
        self.HALOStand['Cl_sp2'][0] = self.C_Cl_sp2.value()
        self.HALOStand['Cl_sp2'][1] = self.H_Cl_sp2.value()
        self.HALOStand['Cl_sp3'][0] = self.C_Cl_sp3.value()
        self.HALOStand['Cl_sp3'][1] = self.H_Cl_sp3.value()
        
        self.HALOStand['Br_sp2'][0] = self.C_Br_sp2.value()
        self.HALOStand['Br_sp2'][1] = self.H_Br_sp2.value()
        self.HALOStand['Br_sp3'][0] = self.C_Br_sp3.value()
        self.HALOStand['Br_sp3'][1] = self.H_Br_sp3.value()        
        
        self.accept()

class CustomTrainingSetDialog(QDialog):
    '''Dialogo para crear un set de training personalizado con las 8 moléculas modelo
    Carga un dialogo diseñando en Qt. 
    '''
    def __init__(self):
        super().__init__()

        # Load the .ui file
        ui_path = os.path.join(os.path.dirname(__file__), 'GUI2', 'custom_trainig_set.ui')
        uic.loadUi(ui_path, self)
        self.setWindowTitle('DP4+ App')

        # Find widgets
        self.mmff_button = self.findChild(QPushButton, 'MMFF')
        self.b3lyp_button = self.findChild(QPushButton, 'B3LYP')
        self.command_line_edit = self.findChild(QLineEdit, 'commandline')
        self.download_button = self.findChild(QPushButton, 'Downldfiles')

        # Initialize state
        self.selected_button = None

        # Connect buttons
        self.mmff_button.clicked.connect(lambda: self.select_button(self.mmff_button))
        self.b3lyp_button.clicked.connect(lambda: self.select_button(self.b3lyp_button))
        self.download_button.clicked.connect(self.download_files)

        self.update_ui()

    def select_button(self, button):
        if self.selected_button:
            self.selected_button.setStyleSheet("")  # Reset style of previously selected button

        self.selected_button = button
        self.selected_button.setStyleSheet("background-color: #90EE90")  # Highlight selected button in green

    def download_files(self):
        if not self.selected_button:
            QMessageBox.warning(self, "Error", "Please select an optimization theory level.")
            return
        
        if 'nmr' not in self.command_line_edit.text().casefold():
            QMessageBox.warning(self, "Error", "Please insert a valid G09 command line")
            return

        self.copy_and_exit()

        # Add any additional code to handle the download here
        
    def change_commandline(self):
        '''Change the command line of .gjc files in the working folder.
        For this, they must be labeled with "# input"'''
        for file in os.scandir('.'):
            if file.is_file(): 
                file_original = file.name
                file = file.name.casefold()
                if 'gjc' in file.split('.')[-1]: 
                    with open(( file_original.rsplit( ".", 1 )[ 0 ] ) + ".gjc", "r+") as f:
                                    content = f.read()
                                    f.seek(0)
                                    f.truncate()
                                    f.write(content.replace('input',self.command_line_edit.text()))
        return
    
    def copy_and_exit(self):
        '''Copy the folder of .gjc files to calculate their nmr and later be 
        used in automatic parameterization.
        Then, it changes its command line with a helper function and finally
        closes the program.
        '''
        desktop = os.path.normpath(os.path.expanduser("~/Desktop"))
        
        if 'B3L' in self.selected_button.text():
            example_fold = os.path.join(os.path.dirname(__file__), "nmr_custom",'opt_B3LYP')
        elif 'MMFF' in self.selected_button.text():
            example_fold = os.path.join(os.path.dirname(__file__), "nmr_custom",'opt_MMFF')

        dst_folder = os.path.join(desktop,"nmr_custom")
        if  os.path.exists(dst_folder):
            dst_folder = f'{dst_folder}_{str(randint(0, 100))}'
        
        try: 
            shutil.copytree(example_fold, dst_folder)
            os.chdir(dst_folder)
            self.change_commandline()
            
            shutil.copy(os.path.join(os.path.dirname(__file__), "nmr_custom",'custom_molecules_set.pdf'), 
                        dst_folder)
            shutil.copy(os.path.join(os.path.dirname(__file__), "nmr_custom",'Data_traning_set.xlsx'), 
                        dst_folder)
            
            QMessageBox.information(self, "DP4+ App", 
                u'Folder Copy \u2713 \n"nmr_custom" has been created on your desktop\nFollow the user guide instructions to process the data.')
            
            self.accept()  # Close the dialog
            
        except : 
            QMessageBox.information(self, "DP4+ App", f'Imposible to download files\nPlease check that your Desktop exists at the location {os.path.dirname(dst_folder)}')
            self.accept()  # Close the dialog
            
        return

    def update_ui(self):
        if self.selected_button:
            self.selected_button.setStyleSheet("background-color: green")

class custom_dp4_tab(QWidget): 
    '''Widget de la función de Custom-DP4+. Los 3 tabs (Calc,Load e Input) se encuentran
    programados aqui diferenciados como 1, 2, y 3 respectivamente. 
    '''
    # signals 
    update_status = pyqtSignal(str)     # update statusBar
    info_pp = pyqtSignal(QMessageBox.Icon, str, str) #Informative PopUp (pp)
    timer = pyqtSignal(bool)
    
    def __init__(self):
        super(custom_dp4_tab, self).__init__()
        tab = os.path.join(os.path.dirname(__file__),'GUI2','custom_tab.ui' )
        uic.loadUi(tab, self)
        
        self.error_flag = False
        self.mode = 'Custom'
        self.HALO = False
                
        # define widgets
        self.examp = self.findChild(QPushButton,'examp_UG')
        self.examp.clicked.connect(self.downld_UG)
        
        # 1) Calc Tab
        # input variables 
        self.dirname1 = ''
        self.xlsname1 = ('','')
        
        # define widgets 
        self.thelev1= self.findChild(QComboBox,'thelev_calc')
        data_base = os.path.join(os.path.dirname(__file__), 'data_base_Custom.xlsx')
        levels = [sheet for sheet in pd.ExcelFile(data_base).sheet_names if 'standard' not in sheet]
        self.thelev1.addItems(levels)
        
        self.dir1 = self.findChild(QPushButton,'dir_calc')
        self.dir_lab1 = self.findChild(QLabel,'dir_lab_calc')
        self.xls1 = self.findChild(QPushButton,'xls_calc')
        self.xls_lab1 = self.findChild(QLabel,'xls_lab_calc')
        self.run1 = self.findChild(QPushButton,'run_calc')
        
        # connect calc widgets 
        self.dir1.clicked.connect(self.selecdir1)
        self.xls1.clicked.connect(self.selecxls1)
        self.run1.clicked.connect(self.runcalc1)
        
        # 2) Input Tab
        self.thelev2 = self.findChild(QLineEdit, 'thelev_input')
        self.C_TMS = self.findChild(QDoubleSpinBox, 'C_TMS')
        self.H_TMS = self.findChild(QDoubleSpinBox, 'H_TMS')
        
        self.n_Csca = self.findChild(QDoubleSpinBox, 'n_Csca')
        self.n_Csp2 = self.findChild(QDoubleSpinBox, 'n_Csp2')
        self.n_Csp3 = self.findChild(QDoubleSpinBox, 'n_Csp3')
        self.n_Hsca = self.findChild(QDoubleSpinBox, 'n_Hsca')
        self.n_Hsp2 = self.findChild(QDoubleSpinBox, 'n_Hsp2')
        self.n_Hsp3 = self.findChild(QDoubleSpinBox, 'n_Hsp3')
        self.m_Csp2 = self.findChild(QDoubleSpinBox, 'm_Csp2')
        self.m_Csp3 = self.findChild(QDoubleSpinBox, 'm_Csp3')
        self.m_Hsp2 = self.findChild(QDoubleSpinBox, 'm_Hsp2')
        self.m_Hsp3 = self.findChild(QDoubleSpinBox, 'm_Hsp3')
        self.s_Csca = self.findChild(QDoubleSpinBox, 's_Csca')
        self.s_Csp2 = self.findChild(QDoubleSpinBox, 's_Csp2')
        self.s_Csp3 = self.findChild(QDoubleSpinBox, 's_Csp3')
        self.s_Hsca = self.findChild(QDoubleSpinBox, 's_Hsca')
        self.s_Hsp2 = self.findChild(QDoubleSpinBox, 's_Hsp2')
        self.s_Hsp3 = self.findChild(QDoubleSpinBox, 's_Hsp3')
        
        self.HeavyAtoms = self.findChild(QPushButton, 'HeavyAtoms')
        self.HeavyAtoms.clicked.connect(self.HALO_PopUp)
        self.HALO_Stand = {'Cl_sp2' : [0,0],   # [C, H] en ese orden
                           'Cl_sp3' : [0,0],
                           'Br_sp2' : [0,0],
                           'Br_sp3' : [0,0],}
        
        self.submit2 = self.findChild(QPushButton,'submit2')
        self.submit2.clicked.connect(self.submit_thelev2)
        
        # 3) Train Tab
        # input variables 
        self.dirname3 = ''
        self.xlsname3 = ('','')
        
        # define widgets 
        self.thelev3= self.findChild(QLineEdit, 'thelev_train')
        self.downld = self.findChild(QPushButton,'download_files')
        self.dir3 =   self.findChild(QPushButton,'dir_train')
        self.dir_lab3 = self.findChild(QLabel,'dir_lab_train')
        self.xls3 = self.findChild(QPushButton,'xls_train')
        self.xls_lab3 = self.findChild(QLabel,'xls_lab_train')
        self.train3 = self.findChild(QPushButton,'train_train')
        
        # connect widgets 
        self.downld.clicked.connect(self.dowload_files)
        self.dir3.clicked.connect(self.selecdir3)
        self.xls3.clicked.connect(self.selecxls3)
        self.train3.clicked.connect(self.train)
               
    # 1) Calc tab funtions ---------------------------------------------
    def selecdir1(self):
        self.dirname1 = QFileDialog.getExistingDirectory(self, 'Select NMR directory')
        if not self.dirname1: 
            self.dir_lab1.setText('Select NMR directory')
            self.run1.setEnabled(False)
            return 
        
        self.update_status.emit('Cheking files ')
        self.timer.emit(True)  # Esto inicia la animación del StatusBar
        
        os.chdir(self.dirname1)
        
        # Create and start the process thread
        self.thread = trap.check_Commmand_Termination_HALO(command = 'nmr', key = 'nmr')
        self.thread.HALO_answer.connect(self.detect_HALO)
        self.thread.finished.connect(self.emit_warning)   # funciona en un pipeline (message passing)
        self.run_thread_a_freeze_tab()
        
        counter = 0
        # Use os.scandir for efficient file iteration
        for entry in os.scandir('.'):
            if entry.is_file():  # Check for files only
                filename = entry.name.casefold()  # Convert to lowercase for case-insensitive search
        
                # Check for nmr, .out, and .log files
                if 'nmr' not in filename:
                    continue  # Skip to next file if not nmr related
                if not (filename.endswith('.out') or filename.endswith('.log')):
                    continue  # Skip to next file if not .out or .log
                counter += 1
                if counter < 2 : continue
                # Files found, break out of the loop
                break  # Exit the loop if required files are found
        
        # Check if required files were found
        if counter < 2:  # Entry points to the last processed file (if any)
            self.timer.emit(False)
            self.update_status.emit('nmr files not found')
            self.dir_lab1.setText('Select NMR directory')
            self.dirname1 = ''
            return
        
        self.dir_lab1.setText(self.dirname1[:3]+'...'+self.dirname1[-50:])
        if self.xlsname1[0] and self.thelev1.currentText(): self.run1.setEnabled(True)    
        
        self.isoms = trap.isomer_count()
        self.timer.emit(False)
        self.update_status.emit(f'Isoms {self.isoms} detected')
        
    def selecxls1(self): 
        self.xlsname1 = QFileDialog.getOpenFileName(self, 'Select correlation file', '', 
                                                    'ExcelFiles (*.xls*) ;; OpenOffice (*.ods) ;; AllFiles(*)')
        if not self.xlsname1[0]: 
            self.xls_lab1.setText( 'Select correlation file')
            self.run1.setEnabled(False)
            return 
        
        self.update_status.emit('Cheking correlation file ')
        self.timer.emit(True)  # Esto inicia la animación del StatusBar
        
        # Create and start the calculation thread
        self.thread = trap.xlsx_trap(self.xlsname1[0], sheets= ['shifts'])
        self.thread.finished.connect(self.emit_error)  # funciona en un pipeline (message passing)
        self.run_thread_a_freeze_tab()
        
        if self.error_flag: 
            self.update_status.emit('Correct the correlation file')
            self.xls_lab1.setText( 'Select correlation file')
            self.error_flag = False
            return 
        
        self.xls_lab1.setText(self.xlsname1[0][:3]+'...'+self.xlsname1[0][-50:])
        if self.dirname1 and self.thelev1.currentText() :  self.run1.setEnabled(True)
        
        self.timer.emit(False)  # Esto inicia la animación del StatusBar
        self.update_status.emit(u'Correlation file loaded \u2713')
        
    def runcalc1(self): 
        '''Función del botón Run del tab Calc. El calculo DP4+ lo realiza en un 
        thread separado que se encuentra en el modulo dp4+ siguiendo la misma 
        estructura que los otros calculos DP4+
        '''
        self.setEnabled(False)
        
        warning = trap.check_labels_and_isom_cant(self.xlsname1[0],'shifts', len(self.isoms))
        if warning: 
            self.emit_error(warning)
            self.update_status.emit(u'Correct the correlation file')
            self.run1.setEnabled(False)
            return
        
        os.chdir(self.dirname1)
        thelev_warn, G09command = trap.the_lev_id('','','','nmr','nmr',only_command=True) 
                
        self.update_status.emit ('DP4+ calculation starting ')
        self.timer.emit(True)  # Inicia la animación del StatusBar
        self.run1.setEnabled(False)
         
        # Interactuar y preguntar cual método utilizar 
        if self.HALO : 
            HALO_answer = show_custom_message(QMessageBox.Warning, "Halogen detected!", 
                                              'Which method do you want to use ? ',
                                              yes='HALO-Custom', no='DP4+')
            if HALO_answer : 
                self.mode = 'HALO-Custom'
                    
        
        # Create and start the calculation thread
        self.thread = simple_dp4_Thread(self.mode, self.dirname1, self.isoms, 
                                    self.xlsname1[0], self.thelev1.currentText(), 
                                    '', '', # solvent, solv_tens
                                    G09command, thelev_warn)
        
        self.thread.message.connect(self.message_pipe_update_status)# funciona en un pipeline (message passing)
        self.thread.finished.connect(self.process_finished)         # funciona en un pipeline (message passing)
        self.run_thread_a_freeze_tab()                              # incluye self.thread.start()
    
    # HALO funtions --------------------------------------------------
    def detect_HALO(self, HALO_answer): 
        self.HALO = True if HALO_answer else False    
        
    # 2) Input tab funtions -----------------------------------------------
    def HALO_PopUp(self): 
        '''Conecta el boton de Download Files con el widget especializado para esto'''
        dialog = HALO_stand_popup(self.HALO_Stand)
        dialog.exec_()
        # Recibir informacion de los tensores y guardarla 
        self.HALO_Stand = dialog.HALOStand
        return
    
    def submit_thelev2(self): 
        '''Controla los parametros ingresados y guarda el nivel de teoría en el 
        programa
        '''
        data = {
            'n': [
                self.n_Csca.value(), self.n_Csp2.value(), self.n_Csp3.value(),
                self.n_Hsca.value(), self.n_Hsp2.value(), self.n_Hsp3.value()
            ],
            'm': [
                0.0, self.m_Csp2.value(), self.m_Csp3.value(),
                0.0, self.m_Hsp2.value(), self.m_Hsp3.value()
            ],
            's': [
                self.s_Csca.value(), self.s_Csp2.value(), self.s_Csp3.value(),
                self.s_Hsca.value(), self.s_Hsp2.value(), self.s_Hsp3.value()
            ]
        }
    
        # Create DataFrame
        parameters = pd.DataFrame(data, index=['Csca', 'Csp2', 'Csp3', 'Hsca', 'Hsp2', 'Hsp3'])
    
        # Check if any 'n' or 's' values are zero
        if any(value == 0 for value in data['n'] + data['s']):
            self.update_status.emit('Invalid parameter/s')
            return
        
        if self.C_TMS.value() == 0 or self.H_TMS.value() == 0: 
            self.update_status.emit('Invalid TMS')
            return
        
        if len(self.thelev2.text()) < 5:
            self.update_status.emit('Invalid name. Too short')
            return
    
        if any(c in '!@#$%^&*()-+?_=,<>/" ' for c in self.thelev2.text()):
            self.update_status.emit('Invalid name. Special character')
            return
    
        if any(c.isupper() for c in self.thelev2.text()):
            self.update_status.emit('Invalid name. Uppercase')
            return
    
        if any (self.thelev2.text() == self.thelev1.itemText(index) for index in range(self.thelev1.count()) ): 
            self.update_status.emit('Level name already exists. Choose other')
            return
        
        # guardar el nivel de teoria             
        gen_out_custom('Input',self.thelev2.text(),
                       self.C_TMS.value(), self.H_TMS.value(), parameters)
        
        # guardar Halo
        save_MSTD_HALO('Input',self.thelev2.text(), self.HALO_Stand)
        
        self.info_pp.emit(QMessageBox.Information,
                          u'Proccess completed \u2713',
                          f'"{self.thelev2.text()}" level has been created.\nFind it in the "Calc" tab.')
    
        self.thelev1.clear()
        data_base = os.path.join(os.path.dirname(__file__), 'data_base_Custom.xlsx')
        levels = [sheet for sheet in pd.ExcelFile(data_base).sheet_names if 'standard' not in sheet]
        self.thelev1.addItems(levels)
        
    # 3) Train Tab ---------------------------------------------------------
    def dowload_files(self): 
        '''Conecta el boton de Download Files con el widget especializado para esto'''
        dialog = CustomTrainingSetDialog()
        dialog.show()
        
    def selecdir3(self):         
        self.dirname3 = QFileDialog.getExistingDirectory(self, 'Select NMR directory')
        if not self.dirname3: 
            self.dir_lab3.setText('Select NMR directory')
            self.train3.setEnabled(False)
            
            self.xls3.setEnabled(False)
            self.xlsname3 = ('','')
            self.xls_lab3.setText( 'Select correlation file')
            self.train3.setEnabled(False)
            return 
        
        self.update_status.emit('Cheking files ')
        self.timer.emit(True)  # Esto inicia la animación del StatusBar
        
        os.chdir(self.dirname3)
        
        # Create and start the process thread
        self.thread = trap.check_Commmand_Termination_HALO(command = 'nmr', key = 'nmr')
        self.thread.finished.connect(self.emit_warning)   # funciona en un pipeline (message passing)
        self.run_thread_a_freeze_tab()
        
        counter = 0
        # Use os.scandir for efficient file iteration
        for entry in os.scandir('.'):
            if entry.is_file():  # Check for files only
                filename = entry.name.casefold()  # Convert to lowercase for case-insensitive search
        
                # Check for nmr, .out, and .log files
                if 'nmr' not in filename:
                    continue  # Skip to next file if not nmr related
                if not (filename.endswith('.out') or filename.endswith('.log')):
                    continue  # Skip to next file if not .out or .log
                counter += 1
                if counter < 2 : continue
                # Files found, break out of the loop
                break  # Exit the loop if required files are found
        
        # Check if required files were found
        if counter < 2:  # Entry points to the last processed file (if any)
            self.timer.emit(False)
            self.update_status.emit('nmr files not found')
            self.dir_lab3.setText('Select NMR directory')
            self.dirname3 = ''
            return
        
        self.dir_lab3.setText(self.dirname3[:3]+'...'+self.dirname3[-50:])
        self.xls3.setEnabled(True)    
        
        self.molecules = trap.isomer_count()
        if not any ('tms' in mol.casefold() for mol in self.molecules ) : 
            self.timer.emit(False)
            self.update_status.emit('TMS (standard) not found')
            self.dir_lab3.setText('Select NMR directory')
            self.dirname3 = ''
            return
        
        self.timer.emit(False)
        self.update_status.emit(f'Molecules {self.molecules} detected')
        
    def selecxls3(self): 
        self.xlsname3 = QFileDialog.getOpenFileName(self, 'Select correlation file', '', 
                                                    'ExcelFiles (*.xls*) ;; OpenOffice (*.ods) ;; AllFiles(*)')
        if not self.xlsname3[0]: 
            self.xls_lab3.setText( 'Select correlation file')
            self.train3.setEnabled(False)
            return 
        
        self.timer.emit(True)  # Esto inicia la animación del StatusBar
        self.update_status.emit('Cheking correlation file ')
        
        # Create and start the calculation thread
        for molec in self.molecules: 
            self.thread = trap.xlsx_trap(self.xlsname3[0], 
                                         sheets= [molec for molec in self.molecules if 'tms' not in molec.casefold()])
            self.thread.finished.connect(self.emit_error)  # funciona en un pipeline (message passing)
            self.run_thread_a_freeze_tab()
        
        if self.error_flag: 
            self.update_status.emit('Correct the correlation file')
            self.xls_lab3.setText( 'Select correlation file')
            self.error_flag = False
            return 
        
        self.xls_lab3.setText(self.xlsname3[0][:3]+'...'+self.xlsname3[0][-50:])
        if self.dirname3 :  self.train3.setEnabled(True)
        
        self.timer.emit(False)  # Esto inicia la animación del StatusBar
        self.update_status.emit(u'Correlation file loaded \u2713')
        
    def train(self): 
        '''Controla los inputs y ejecuta el modulo de entrenamiento para obtener
        los parametros de distribución. Esto lo hace en un thread separdo que luego 
        pasa los resultados a la función submitlevel para guarda la info. 
        '''
        if len(self.thelev3.text()) < 5:
            self.update_status.emit('Invalid name. Too short')
            return
    
        if any(c in '!@#$%^&*()-+?_=,<>/" ' for c in self.thelev3.text()):
            self.update_status.emit('Invalid name. Special character')
            return
    
        if any(c.isupper() for c in self.thelev3.text()):
            self.update_status.emit('Invalid name. Uppercase')
            return
    
        if any (self.thelev3.text() == self.thelev1.itemText(index) for index in range(self.thelev1.count()) ): 
            self.update_status.emit('Level name already exists. Choose other')
            return
        
        # Create and start the calculation thread
        os.chdir(self.dirname3)
        self.timer.emit(True)
        self.thread = train_Thread(self.thelev3.text(),
                                   self.dirname3, self.xlsname3[0], 
                                   self.molecules )
        
        self.thread.message.connect(self.message_pipe_update_status)# funciona en un pipeline (message passing)
        self.thread.correlation_warn.connect(self.emit_warning)
        self.thread.finished.connect(self.process_finished)         # funciona en un pipeline (message passing)
        self.thread.results.connect(self.submit_thelev3)
        self.run_thread_a_freeze_tab()                              # incluye self.thread.start()
        
    def submit_thelev3(self, parameters:pd.DataFrame, standard:dict, 
                       small_sample:bool, MSTD: dict): 
        '''Salva la información del entrenamiento en el thread de custom'''
        result = show_custom_message(QMessageBox.Information,
                                     'Attention',
                                     "Very few sampling points have been provided\n"
                                    "They may be insufficient to correctly estimate the degrees of freedom\n"
                                    "It is advisable to use averaged degrees of freedom.\n"
                                    "How do you want to proceed?", yes = 'Use AVERAGE values', no = 'Use REAL values')
        if result : 
            parameters.loc['Csca','n'] = 7
            parameters.loc['Csp2','n'] = 8
            parameters.loc['Csp3','n'] = 10
            parameters.loc['Hsca','n'] = 4
            parameters.loc['Hsp2','n'] = 8
            parameters.loc['Hsp3','n'] = 4
        
        os.chdir(self.dirname3)
        _, G09command = trap.the_lev_id('','','','nmr','nmr',only_command=True) 
        
        # guardar el nivel de teoria                     
        gen_out_custom(G09command,self.thelev3.text(),
                       standard['C'], standard['H'], parameters)
        
        # guardar Halo
        save_MSTD_HALO(G09command ,self.thelev3.text(), MSTD)
        
        self.thelev1.clear()
        data_base = os.path.join(os.path.dirname(__file__), 'data_base_Custom.xlsx')
        levels = [sheet for sheet in pd.ExcelFile(data_base).sheet_names if 'standard' not in sheet]
        self.thelev1.addItems(levels)
        
        self.update_status.emit('Training completed')
        
        self.info_pp.emit(QMessageBox.Information,
                          u'Proccess completed \u2713',
                          f'"{self.thelev3.text()}" level has been created.\nFind it in the "Calc" tab.')
    
    
    def downld_UG(self): 
        '''Copia un ejemplo de entrenamiento'''
        desktop = os.path.normpath(os.path.expanduser("~/Desktop"))
        mm_example = os.path.join(os.path.dirname(__file__), "example_custom_training")
        
        self.timer.emit(True)
        self.update_status.emit('Dowloading example ')
        self.thread = DownloadThread(mm_example, desktop)
        self.thread.fail_signal.connect(self.download_fail)
        self.thread.finished_signal.connect(self.thread_finished)
        self.thread.start()
        
    def download_fail(self, dst_folder): 
        self.timer.emit(False)
        self.info_pp.emit(QMessageBox.Warning, 'Download failed', 
          f'Download failed. Please check that your Desktop exists at the location {os.path.dirname(dst_folder)}')
        self.update_status.emit('Download failed')
        
    def thread_finished(self, dst_folder):
        self.timer.emit(False)
        self.update_status.emit(u'Example downloaded \u2713')
        self.open_example(dst_folder)    
        
    def open_example(self, path): 
        system_name = sys.platform
        if system_name == "win32":
            subprocess.run(["explorer", path])
        elif system_name == "darwin":  # macOS
            subprocess.run(["open", path])
        elif system_name == "linux":
            subprocess.run(["xdg-open", path])
    
    # pipelines (message passing) and auxiliar funtions --------------------
    def emit_warning(self, warn):
        self.setEnabled(True)
        
        if not warn : return 
        
        self.info_pp.emit(QMessageBox.Warning, warn, '')
        
    def emit_error(self, warn):
        self.setEnabled(True)
        
        if not warn : return 
        
        self.info_pp.emit(QMessageBox.Critical, warn, '')
        self.error_flag = True
        
    def process_finished(self, signs : dict ):
        
        if not signs : 
            self.setEnabled(True)
            return 
        
        if 'aborted' in signs['statusBar']: 
            icon = QMessageBox.Critical 
            self.dirname1 = ''
            self.dir_lab1.setText('Select NMR directory')
            self.xlsname1 = ('','')
            self.xls_lab1.setText( 'Select correlation file')
                  
        else : 
            icon = QMessageBox.Information
        
        self.update_status.emit(signs['statusBar'])
        
        self.info_pp.emit(icon ,signs['popupTitle'],signs['popupText'] )
        
        self.mode = 'Custom'
        self.HALO = False
        self.setEnabled(True)

    def message_pipe_update_status(self, message): 
        self.update_status.emit(message)
        
    def run_thread_a_freeze_tab(self): 
        self.setEnabled(False)
        
        event_loop = QEventLoop()  # Create an event loop
        
        self.thread.finished.connect(event_loop.quit) #connect the event loop quit signal to the thread finished signal
        self.thread.start() # Start the thread
        
        event_loop.exec_()  # Start the event loop
        time.sleep(1)
        self.setEnabled(True) # Enable the tab after the thread finishes
     
# -----------------------------------------------------------------------------
class mm_dp4_tab(QWidget):
    # signals 
    update_status = pyqtSignal(str)     # update statusBar
    info_pp = pyqtSignal(QMessageBox.Icon, str, str) #Informative PopUp (pp)
    timer = pyqtSignal(bool)
    
    def __init__(self):
        super(mm_dp4_tab, self).__init__()
        tab = os.path.join(os.path.dirname(__file__),'GUI2','mm_dp4_tab.ui' )
        uic.loadUi(tab, self)
        
        self.error_flag = False
        
        #input variables 
        self.dirname = ''
        self.xlsname = ('','')
        self.energyname = ''
        self.solvname = None
        
        self.HALO = False
        
        # define widgets
        self.examp = self.findChild(QPushButton,'examp_UG') 
        
        self.dir = self.findChild(QPushButton,'dir')
        self.xls = self.findChild(QPushButton,'xls')
        self.run = self.findChild(QPushButton,'run')
        
        self.dir_lab = self.findChild(QLabel,'dir_lab')
        self.xls_lab = self.findChild(QLabel,'xls_lab')
        
        self.func = self.findChild(QComboBox,'func')
        self.basis = self.findChild(QComboBox,'basis')
        self.solv = self.findChild(QComboBox,'solv')
        self.solvent= self.findChild(QComboBox,'solvent')
        
        # funtions
        self.examp.clicked.connect(self.downld_UG)   
        
        self.dir.clicked.connect(self.selecdir)
        self.xls.clicked.connect(self.selecxls)
        self.solv.currentIndexChanged.connect(self.solvdecision)
        self.solvent.currentIndexChanged.connect(self.customsolv)
        self.run.clicked.connect(self.runcalc)
        
    def selecdir(self):
        self.dirname = QFileDialog.getExistingDirectory(self, 'Select NMR directory')
        if not self.dirname: 
            self.dir_lab.setText('Select NMR directory')
            self.run.setEnabled(False)
            return 
        
        self.update_status.emit('Cheking files ')
        self.timer.emit(True)  # Esto inicia la animación del StatusBar
        
        os.chdir(self.dirname)
        
        # Create and start the process thread
        self.thread = trap.check_Commmand_Termination_HALO(command = 'nmr', key = 'nmr')
        self.thread.HALO_answer.connect(self.detect_HALO)
        self.thread.finished.connect(self.emit_warning)   # funciona en un pipeline (message passing)
        self.run_thread_a_freeze_tab()
        
        counter = 0
        # Use os.scandir for efficient file iteration
        for entry in os.scandir('.'):
            if entry.is_file():  # Check for files only
                filename = entry.name.casefold()  # Convert to lowercase for case-insensitive search
        
                # Check for nmr, .out, and .log files
                if 'nmr' not in filename:
                    continue  # Skip to next file if not nmr related
                if not (filename.endswith('.out') or filename.endswith('.log')):
                    continue  # Skip to next file if not .out or .log
                counter += 1
                if counter < 2 : continue
                # Files found, break out of the loop
                break  # Exit the loop if required files are found
        
        # Check if required files were found
        if counter < 2:  # Entry points to the last processed file (if any)
            self.timer.emit(False)
            self.update_status.emit('nmr files not found')
            self.dir_lab.setText('Select NMR directory')
            self.dirname = ''
            return
        
        self.dir_lab.setText(self.dirname[:3]+'...'+self.dirname[-50:])
        if self.xlsname[0] : self.run.setEnabled(True)    
        
        self.isoms = trap.isomer_count()
        self.timer.emit(False)
        self.update_status.emit(f'Isoms {self.isoms} detected')
        
        
    def selecxls(self): 
        self.xlsname = QFileDialog.getOpenFileName(self, 'Select correlation file', '', 
                                                    'ExcelFiles (*.xls*) ;; OpenOffice (*.ods) ;; AllFiles(*)'
                                                    )
        if not self.xlsname[0]: 
            self.xls_lab.setText( 'Select correlation file')
            self.run.setEnabled(False)
            return 
        
        self.update_status.emit('Cheking correlation file ')
        self.timer.emit(True)  # Esto inicia la animación del StatusBar
        
        # Create and start the calculation thread
        self.thread = trap.xlsx_trap(self.xlsname[0], sheets= ['shifts'])
        self.thread.finished.connect(self.emit_error)  # funciona en un pipeline (message passing)
        self.run_thread_a_freeze_tab()
        
        if self.error_flag: 
            self.update_status.emit('Correct the correlation file')
            self.xls_lab.setText( 'Select correlation file')
            self.error_flag = False
            return 
        
        self.xls_lab.setText(self.xlsname[0][:3]+'...'+self.xlsname[0][-50:])
        if self.dirname :  self.run.setEnabled(True)
        
        self.timer.emit(False)  # Esto inicia la animación del StatusBar
        self.update_status.emit(u'Correlation file loaded \u2713')
        
    def solvdecision(self): 
        if self.solv.currentText() == 'GAS': 
            self.solvent.setEnabled(False)
            self.solvent.setCurrentIndex(0)
        else: 
            self.solvent.setEnabled(True)
            self.solvent.setCurrentIndex(1)
            
    def customsolv(self): 
        if self.solvent.currentText() != 'Other': 
            self.solvname = None
            self.update_status.emit('')
            return
        
        result, tensorC, tensorH = self.ask_solvent_tensors_PopUp()

        if result == QDialog.Accepted and tensorC and tensorH:
            self.solvname = {'C':float(tensorC) , 'H' : float(tensorH)}
            self.update_status.emit(f"Tensor C: {tensorC}, Tensor H: {tensorH} loaded") 
        else: 
            self.update_status.emit("No tensors enter. Select solvent") 
            self.solvname = None
            
    def runcalc(self): 
        
        self.setEnabled(False)
        
        if not self.solvname and self.solvent.currentText() == 'Other': 
            self.emit_warning('Solvent is required to proceed')
            self.update_status.emit("Solvent is required to proceed") 
            return
        
        warning = trap.check_labels_and_isom_cant(self.xlsname[0],'shifts', len(self.isoms))
        if warning: 
            self.emit_error(warning)
            self.update_status.emit(u'Correct the correlation file')
            self.run.setEnabled(False)
            return
        
        if self.solv.currentText() != 'GAS' and  self.solvent.currentText() == '': 
            self.update_status.emit('Select solvent')
            self.emit_warning('Select solvent')
            return
        
        os.chdir(self.dirname)
        thelev_warn, G09command = trap.the_lev_id(self.func.currentText(),
                                  self.basis.currentText(),
                                  self.solv.currentText(),
                                  'nmr','nmr',
                                  solvent = self.solvent.currentText())  
        if thelev_warn: 
            answer = self.thelev_warning_decision(thelev_warn, G09command)
            
            if not answer:  # answer to continue even though the inconsistence     
                self.update_status.emit(u'Theory level entered does not match with the files \u2716')
                self.setEnabled(True)
                return 
        
        self.update_status.emit ('DP4+ calculation starting ')
        self.timer.emit(True)  # Inicia la animación del StatusBar
        self.run.setEnabled(False)
        
        # Concatenate the theory level
        if 'GAS' in self.solv.currentText():
            the_lev = self.func.currentText()+"."+self.basis.currentText()
        else: 
            the_lev = self.func.currentText()+"."+self.basis.currentText()+"."+self.solv.currentText()
        
        
        # Interactuar y preguntar cual método utilizar 
        calc_mode = 'MM'
        if self.HALO : 
            HALO_answer = show_custom_message(QMessageBox.Warning, "Halogen detected!", 
                                              'Which method do you want to use ? ',
                                              yes='HALO-MM-DP4', no='DP4+')
            if HALO_answer : 
                calc_mode = 'HALO-MM'
        
        # Create and start the calculation thread
        self.thread = simple_dp4_Thread(calc_mode, self.dirname, self.isoms, 
                                    self.xlsname[0], the_lev, 
                                    self.solvent.currentText(), self.solvname,
                                    G09command, thelev_warn)
        
        self.thread.message.connect(self.message_pipe_update_status)# funciona en un pipeline (message passing)
        self.thread.finished.connect(self.process_finished)         # funciona en un pipeline (message passing)
        self.run_thread_a_freeze_tab()                              # incluye self.thread.start()
    
    def downld_UG(self): 
        desktop = os.path.normpath(os.path.expanduser("~/Desktop"))
        mm_example = os.path.join(os.path.dirname(__file__), "example_nmr_mm")
        
        self.timer.emit(True)
        self.update_status.emit('Dowloading example ')
        self.thread = DownloadThread(mm_example, desktop)        
        self.thread.fail_signal.connect(self.download_fail)
        self.thread.finished_signal.connect(self.thread_finished)
        self.thread.start()
        
    def download_fail(self, dst_folder): 
        self.timer.emit(False)
        self.info_pp.emit(QMessageBox.Warning, 'Download failed', 
          f'Download failed. Please check that your Desktop exists at the location {os.path.dirname(dst_folder)}')
        self.update_status.emit('Download failed')
        
    def thread_finished(self, dst_folder):
        self.timer.emit(False)
        self.update_status.emit(u'Example downloaded \u2713')
        self.open_example(dst_folder)    
        
    def open_example(self, path): 
        system_name = sys.platform
        if system_name == "win32":
            subprocess.run(["explorer", path])
        elif system_name == "darwin":  # macOS
            subprocess.run(["open", path])
        elif system_name == "linux":
            subprocess.run(["xdg-open", path])
        
    # HALO funtions --------------------------------------------------
    def detect_HALO(self, HALO_answer): 
        self.HALO = True if HALO_answer else False
        
    # pipelines (message passing) and auxiliar funtions --------------------
    def emit_warning(self, warn):
        self.setEnabled(True)
        
        if not warn : return 
        
        self.info_pp.emit(QMessageBox.Warning, warn, '')
        
    def emit_error(self, warn):
        self.setEnabled(True)
        
        if not warn : return 
        
        self.info_pp.emit(QMessageBox.Critical, warn, '')
        self.error_flag = True
        
    def process_finished(self, signs : dict ):
        
        if 'aborted' in signs['statusBar']: 
            icon = QMessageBox.Critical 
            self.dirname = ''
            self.dir_lab.setText('Select NMR directory')
            self.xlsname = ('','')
            self.xls_lab.setText( 'Select correlation file')
                  
        else : 
            icon = QMessageBox.Information
        
        self.update_status.emit(signs['statusBar'])
        
        self.info_pp.emit(icon ,signs['popupTitle'],signs['popupText'] )
        
        self.setEnabled(True)

    def message_pipe_update_status(self, message): 
        self.update_status.emit(message)
        
    def run_thread_a_freeze_tab(self): 
        self.setEnabled(False)
        
        event_loop = QEventLoop()  # Create an event loop
        
        self.thread.finished.connect(event_loop.quit) #connect the event loop quit signal to the thread finished signal
        self.thread.start() # Start the thread
        
        event_loop.exec_()  # Start the event loop
        
        self.setEnabled(True) # Enable the tab after the thread finishes
    
    def ask_solvent_tensors_PopUp(self):
        answer, tensorC, tensorH = SolventTensorsDialog()
        return answer, tensorC, tensorH
    
    def thelev_warning_decision(self, warns, G09command):

        display = '''
        The selected theory level does not match the one in the calculations.
        It is recommended to correct the following inconsistency before continuing:'''
        for i in warns : 
            display = display + '\n' + '\t *' +str(i)
            
        display = display + '\n\nCalculations commandline is:\n' + G09command
        
        display = display +'\nDo you want to continue with the calculation despite the inconsistencies found?'
        
        result = show_custom_message(QMessageBox.Warning, "Warning!", display)
        
        if result :
            return True
        else:
            return False 
# -----------------------------------------------------------------------------        
class UG_dp4plus_popup(QDialog):
    update_status = pyqtSignal(bool)
    fail_signal = pyqtSignal(str)
    
    def __init__(self):
        super(UG_dp4plus_popup, self).__init__()
        
        GUI = os.path.join(os.path.dirname(__file__),'GUI2','dp4_UG.ui' )
        uic.loadUi(GUI, self)
        self.setWindowTitle('DP4+ App')
        
        # define buttons 
        self.nmr_only_button = self.findChild(QPushButton,'nmr_only')
        self.two_files_button = self.findChild(QPushButton,'two_files')
        self.link_button = self.findChild(QPushButton,'link')
        self.HALO_button = self.findChild(QPushButton,'halo')
        
        # connect funtions 
        self.nmr_only_button.clicked.connect(self.nmr_only_dwload)
        self.two_files_button.clicked.connect(self.two_files_dwload)
        self.link_button.clicked.connect(self.link_dwload)
        self.HALO_button.clicked.connect(self.HALO_dwload)
        
        # define paths  
        self.desktop = os.path.normpath(os.path.expanduser("~/Desktop"))
        self.nmr_only =os.path.join(os.path.dirname(__file__), "example_nmr_only")
        self.two_files = os.path.join(os.path.dirname(__file__), "example_nmr_gibbs")
        self.link = os.path.join(os.path.dirname(__file__), "example_link")
        self.HALO = os.path.join(os.path.dirname(__file__), "example_HALO")
        
    def nmr_only_dwload(self): 
        self.start_thread(self.nmr_only)

    def two_files_dwload(self): 
        self.start_thread(self.two_files)
        
    def link_dwload(self): 
        self.start_thread(self.link)
        
    def HALO_dwload(self): 
        self.start_thread(self.HALO)
        
    def start_thread(self, src_folder):
        self.update_status.emit(True)
        self.thread = DownloadThread(src_folder, self.desktop)      
        self.thread.fail_signal.connect(self.download_fail)
        self.thread.finished_signal.connect(self.thread_finished)
        self.thread.start()
        
    def download_fail(self, dst_folder): 
        self.fail_signal.emit(dst_folder)
        
    def thread_finished(self, dst_folder):
        self.update_status.emit(False)
        self.open_example(dst_folder)    
        
    def open_example(self, path): 
        system_name = sys.platform
        if system_name == "win32":
            subprocess.run(["explorer", path])
        elif system_name == "darwin":  # macOS
            subprocess.run(["open", path])
        elif system_name == "linux":
            subprocess.run(["xdg-open", path])

class dp4_tab(QWidget):
    # signals 
    update_status = pyqtSignal(str)     # update statusBar
    info_pp = pyqtSignal(QMessageBox.Icon, str, str) #Informative PopUp (pp)
    timer = pyqtSignal(bool)
    
    def __init__(self):
        super(dp4_tab, self).__init__()
        tab = os.path.join(os.path.dirname(__file__),'GUI2','dp4_tab.ui' )
        uic.loadUi(tab, self)
        
        self.error_flag = False
        
        # 1) DP4+ Tab ---------------------------------------------------------
        #input variables 
        self.dirname = ''
        self.xlsname = ('','')
        self.energyname = ''
        self.solvname = None
        self.HALO = False
        
        # define widgets
        self.examp = self.findChild(QPushButton,'examp_UG') 
        
        self.dir = self.findChild(QPushButton,'dir')
        self.xls = self.findChild(QPushButton,'xls')
        self.energy = self.findChild(QPushButton,'energy')
        self.run = self.findChild(QPushButton,'run')
        
        self.dir_lab = self.findChild(QLabel,'dir_lab')
        self.xls_lab = self.findChild(QLabel,'xls_lab')
        self.energy_lab = self.findChild(QLabel,'energy_lab')
        
        self.func = self.findChild(QComboBox,'func')
        self.basis = self.findChild(QComboBox,'basis')
        self.solv = self.findChild(QComboBox,'solv')
        self.solvent = self.findChild(QComboBox,'solvent')
        
        self.SCF_NMR = self.findChild(QRadioButton,'SCF_NMR')
        self.SCF_Energy = self.findChild(QRadioButton,'SCF_Energy')
        self.Gibbs = self.findChild(QRadioButton,'Gibbs')
        self.link = self.findChild(QCheckBox,'link_checkBox')
        
        # funtions
        self.examp.clicked.connect(self.open_UG)   #MODIFICAR X EL CORRECTO
        
        self.dir.clicked.connect(self.selecdir)
        self.xls.clicked.connect(self.selecxls)
        self.energy.clicked.connect(self.selecenergy)
        self.run.clicked.connect(self.runcalc)
        
        self.solv.currentIndexChanged.connect(self.solvdecision)
        
        self.solvent.currentIndexChanged.connect(self.customsolv)
        
        self.SCF_NMR.clicked.connect(self.energydecision)
        self.SCF_Energy.clicked.connect(self.energydecision)
        self.Gibbs.clicked.connect(self.energydecision)
        self.link.toggled.connect(self.energydecision)
        
    # 1) DP4+ Tab ---------------------------------------------------------        
    def open_UG(self):
        self.UG_PopUp = UG_dp4plus_popup()
        self.UG_PopUp.fail_signal.connect(self.download_fail)
        self.UG_PopUp.update_status.connect(self.UG_status)
        self.UG_PopUp.show()
        
    def download_fail(self, dst_folder): 
        self.info_pp.emit(QMessageBox.Warning, 'Download failed', 
          f'Download failed. Please check that your Desktop exists at the location {os.path.dirname(dst_folder)}')
        self.update_status.emit('Dowload failed')
    
    def UG_status(self, signal:bool): 
        if signal : 
            self.update_status.emit('Dowloading example')
            self.timer.emit(True)
        
        else: 
            self.timer.emit(False)
            self.update_status.emit(u'Example downloaded \u2713')
            
    def selecdir(self):
        self.dirname = QFileDialog.getExistingDirectory(self, 'Select NMR directory')
        if not self.dirname: 
            self.dir_lab.setText('Select NMR directory')
            self.run.setEnabled(False)
            return 
        
        self.update_status.emit('Cheking files ')
        self.timer.emit(True)  # Esto inicia la animación del StatusBar
        
        os.chdir(self.dirname)
        
        # Create and start the process thread
        self.thread = trap.check_Commmand_Termination_HALO(command = 'nmr', key = 'nmr')
        self.thread.HALO_answer.connect(self.detect_HALO)
        self.thread.finished.connect(self.emit_warning)   # funciona en un pipeline (message passing)
        self.run_thread_a_freeze_tab()
        # self.error_flag = False
        
        counter = 0
        # Use os.scandir for efficient file iteration
        for entry in os.scandir('.'):
            if entry.is_file():  # Check for files only
                filename = entry.name.casefold()  # Convert to lowercase for case-insensitive search
        
                # Check for nmr, .out, and .log files
                if 'nmr' not in filename:
                    continue  # Skip to next file if not nmr related
                if not (filename.endswith('.out') or filename.endswith('.log')):
                    continue  # Skip to next file if not .out or .log
                counter += 1
                if counter < 2 : continue
                # Files found, break out of the loop
                break  # Exit the loop if required files are found
        
        # Check if required files were found
        if counter < 2:  # Entry points to the last processed file (if any)
            self.timer.emit(False)
            self.update_status.emit('nmr files not found')
            self.dir_lab.setText('Select NMR directory')
            self.dirname = ''
            return
        
        self.dir_lab.setText(self.dirname[:3]+'...'+self.dirname[-50:])
        if self.xlsname[0] and self.SCF_NMR.isChecked() : self.run.setEnabled(True)    
        if not self.SCF_NMR.isChecked() and self.xlsname[0] and self.energyname : self.run.setEnabled(True) 
        if not self.SCF_NMR.isChecked() and self.xlsname[0] and self.link.isChecked() : self.run.setEnabled(True) 
        
        self.isoms = trap.isomer_count()
        self.timer.emit(False)
        self.update_status.emit(f'Isoms {self.isoms} detected')
        
    def selecxls(self): 
        self.xlsname = QFileDialog.getOpenFileName(self, 'Select correlation file', '', 
                                                    'ExcelFiles (*.xls*) ;; OpenOffice (*.ods) ;; AllFiles(*)'
                                                    )
        if not self.xlsname[0]: 
            self.xls_lab.setText( 'Select correlation file')
            self.run.setEnabled(False)
            return 
        
        self.update_status.emit('Cheking correlation file ')
        self.timer.emit(True)  # Esto inicia la animación del StatusBar
        
        # Create and start the calculation thread
        self.thread = trap.xlsx_trap(self.xlsname[0], sheets= ['shifts'])
        self.thread.finished.connect(self.emit_error)  # funciona en un pipeline (message passing)
        self.run_thread_a_freeze_tab()
        
        if self.error_flag: 
            self.update_status.emit('Correct the correlation file')
            self.xls_lab.setText( 'Select correlation file')
            self.error_flag = False
            return 
        
        self.xls_lab.setText(self.xlsname[0][:3]+'...'+self.xlsname[0][-50:])
        if self.dirname and self.SCF_NMR.isChecked():  self.run.setEnabled(True)
        if not self.SCF_NMR.isChecked() and self.dirname and self.energyname : self.run.setEnabled(True)  
        if not self.SCF_NMR.isChecked() and self.dirname and self.link.isChecked() : self.run.setEnabled(True)

        self.timer.emit(False)  # Esto inicia la animación del StatusBar
        self.update_status.emit(u'Correlation file loaded \u2713')
  
    def selecenergy(self):
        self.energyname = QFileDialog.getExistingDirectory(self, 'Select energy directory')
        self.energy_lab.setText(self.energyname[:3]+'...'+self.energyname[-50:])
        if not self.energyname: 
            self.energy_lab.setText( 'Select energy directory')
            self.run.setEnabled(False)
            self.link.setEnabled(True)
            return
        
        self.update_status.emit('Cheking files ')
        self.timer.emit(True)  # Esto inicia la animación del StatusBar
        
        os.chdir(self.energyname)
        
        command = 'freq' if self.Gibbs.isChecked() else ''

        self.thread = trap.check_Commmand_Termination_HALO(command = command, key = 'energy' )    
        self.thread.finished.connect(self.emit_warning)  # funciona en un pipeline (message passing)
        self.run_thread_a_freeze_tab()
        # self.error_flag = False
        
        counter = 0
        # Use os.scandir for efficient file iteration
        for entry in os.scandir('.'):
            if entry.is_file():  # Check for files only
                filename = entry.name.casefold()  # Convert to lowercase for case-insensitive search
        
                # Check for nmr, .out, and .log files
                if 'energy' not in filename:
                    continue  # Skip to next file if not nmr related
                if not (filename.endswith('.out') or filename.endswith('.log')):
                    continue  # Skip to next file if not .out or .log
                counter += 1
                if counter < 2 : continue
                # Files found, break out of the loop
                break  # Exit the loop if required files are found
        
        # Check if required files were found
        if counter < 2:  # Entry points to the last processed file (if any)
            self.timer.emit(False)
            self.update_status.emit('energy files not found')
            self.energy_lab.setText( 'Select energy directory')
            self.energyname = ''
            self.run.setEnabled(False)
            return
        
        self.link.setEnabled(False)
        self.link.setChecked(False)
        if self.xlsname[0] and  self.dirname: self.run.setEnabled(True)
                
        self.timer.emit(False)
        self.update_status.emit('energy files loaded')
        
    def solvdecision(self): 
        if self.solv.currentText() == 'GAS': 
            self.solvent.setEnabled(False)
            self.solvent.setCurrentIndex(0)
        else: 
            self.solvent.setEnabled(True)
            self.solvent.setCurrentIndex(1)
            
    def customsolv(self): 
        if self.solvent.currentText() != 'Other': 
            self.solvname = None
            self.update_status.emit('')
            return
        
        result, tensorC, tensorH = self.ask_solvent_tensors_PopUp()

        if result == QDialog.Accepted and tensorC and tensorH:
            self.solvname = {'C':float(tensorC) , 'H' : float(tensorH)}
            self.update_status.emit(f"Tensor C: {tensorC}, Tensor H: {tensorH} loaded") 
        else: 
            self.update_status.emit("No tensors enter. Select solvent") 
            self.solvname = None
        
    def energydecision(self): 
        self.update_status.emit('')
        
        if self.SCF_NMR.isChecked(): 
            self.energy.setEnabled(False)
            self.energy_lab.setText('')
            self.link.setEnabled(False)
            self.link.setChecked(False)
            self.energyname = ''
            if self.xlsname[0] and  self.dirname: self.run.setEnabled(True) 
            return
            
        else: 
            self.energyname = ''
            self.energy.setEnabled(True)
            self.energy_lab.setText('')
            
            if self.energy_lab.text() == '': 
                self.energy_lab.setText('Select energy directory')
                self.link.setEnabled(True)
                self.run.setEnabled(False)
                self.update_status.emit('')
            
            if self.link.isChecked(): 
                self.energy.setEnabled(False)
                self.energy_lab.setText('')
                self.update_status.emit('Link mode selected')
                if self.xlsname[0] and  self.dirname: self.run.setEnabled(True)
        
    def runcalc(self): 
        
        self.setEnabled(False)
        
        if not self.solvname and self.solvent.currentText() == 'Other': 
            self.emit_warning('Solvent is required to proceed')
            self.update_status.emit("Solvent is required to proceed") 
            return
        
        warning = trap.check_labels_and_isom_cant(self.xlsname[0],'shifts', len(self.isoms))
        if warning: 
            self.emit_error(warning)
            self.update_status.emit(u'Correct the correlation file')
            self.run.setEnabled(False)
            return
        
        if self.solv.currentText() != 'GAS' and  self.solvent.currentText() == '': 
            self.update_status.emit('Select solvent')
            self.emit_warning('Select solvent')
            return
        
        os.chdir(self.dirname)
        thelev_warn, nmr_command = trap.the_lev_id(self.func.currentText(),
                                  self.basis.currentText(),
                                  self.solv.currentText(),
                                  'nmr','nmr',
                                  solvent=self.solvent.currentText())  
        if thelev_warn: 
            answer = self.thelev_warning_decision(thelev_warn, nmr_command)
            
            if not answer:  # answer to continue even though the inconsistence     
                self.update_status.emit(u'Theory level entered does not match with the files \u2716')
                self.setEnabled(True)
                return 
        
        self.update_status.emit ('DP4+ calculation starting ')
        self.timer.emit(True)  # Inicia la animación del StatusBar
        self.run.setEnabled(False)
        
        # Concatenate the theory level
        if 'GAS' in self.solv.currentText():
            the_lev = self.func.currentText()+"."+self.basis.currentText()
        else: 
            the_lev = self.func.currentText()+"."+self.basis.currentText()+"."+self.solv.currentText()
            
        # Translate the Energy Radio Button 
        if self.SCF_NMR.isChecked(): 
            energy = 'nmr'
        else : 
            energy = 'energy' if self.SCF_Energy.isChecked() else 'gibbs'
            
        # Translate the optimization selection - link or folder
        energy_info = 'link' if self.link.isChecked() else self.energyname
        
        # Interactuar y preguntar cual método utilizar 
        calc_mode = 'QM'
        if self.HALO : 
            HALO_answer = show_custom_message(QMessageBox.Warning, "Halogen detected!", 
                                              'Which method do you want to use ? ',
                                              yes='HALO-DP4+', no='DP4+')
            if HALO_answer : 
                calc_mode = 'HALO'
        
        # Create and start the calculation thread
        self.thread = gibbs_dp4_Thread(calc_mode, self.dirname, self.isoms, 
                                     self.xlsname[0], the_lev, 
                                     self.solvent.currentText(), self.solvname,
                                     energy , energy_info, 
                                     nmr_command, thelev_warn)
        
        self.thread.message.connect(self.message_pipe_update_status)# funciona en un pipeline (message passing)
        self.thread.finished.connect(self.process_finished)         # funciona en un pipeline (message passing)
        self.run_thread_a_freeze_tab()                              # incluye self.thread.start()
    
    # HALO funtions --------------------------------------------------
    def detect_HALO(self, HALO_answer): 
        self.HALO = True if HALO_answer else False
            
    # pipelines (message passing) and auxiliar funtions --------------------
    def emit_warning(self, warn):
        self.setEnabled(True)
        
        if not warn : return 
        
        self.info_pp.emit(QMessageBox.Warning, warn, '')
        
    def emit_error(self, warn):
        self.setEnabled(True)
        
        if not warn : return 
        
        self.info_pp.emit(QMessageBox.Critical, warn, '')
        self.error_flag = True
        
    def process_finished(self, signs : dict ):
        
        if 'aborted' in signs['statusBar']: 
            icon = QMessageBox.Critical 
            self.dirname = ''
            self.dir_lab.setText('Select NMR directory')
            self.xlsname = ('','')
            self.xls_lab.setText( 'Select correlation file')
            self.energyname = ''
            
            if not self.link.isChecked() : 
                self.energyname = ''
                self.energy_lab.setText('Select energy directory')
            
        else : 
            icon = QMessageBox.Information
        
        self.update_status.emit(signs['statusBar'])
        
        self.info_pp.emit(icon ,signs['popupTitle'],signs['popupText'] )
        
        self.setEnabled(True)
        # self.run.setEnabled(True)
        
    def message_pipe_update_status(self, message): 
        self.update_status.emit(message)
        
    def run_thread_a_freeze_tab(self): 
        self.setEnabled(False)
        
        event_loop = QEventLoop()  # Create an event loop
        
        self.thread.finished.connect(event_loop.quit) #connect the event loop quit signal to the thread finished signal
        self.thread.start() # Start the thread
        
        event_loop.exec_()  # Start the event loop
        
        self.setEnabled(True) # Enable the tab after the thread finishes
    
    def ask_solvent_tensors_PopUp(self):
        answer, tensorC, tensorH = SolventTensorsDialog()
        return answer, tensorC, tensorH
        
    def thelev_warning_decision(self, warns, G09command):

        display = '''
        The selected theory level does not match the one in the calculations.
        It is recommended to correct the following inconsistency before continuing:'''
        for i in warns : 
            display = display + '\n' + '\t *' +str(i)
            
        display = display + '\n\nCalculations commandline is:\n' + G09command
        
        display = display +'\nDo you want to continue with the calculation despite the inconsistencies found?'
        
        result = show_custom_message(QMessageBox.Warning, "Warning!", display)
        
        if result :
            return True
        else:
            return False      

# -------------------------------------------------------------------------
def main(): 

    # import webbrowser
    # try:
    #     webbrowser.open('https://www.youtube.com/watch?v=wi8yJdKO1j0')
    # except webbrowser.Error as e:
    #     pass  


    app = QApplication(sys.argv)
    UIWindow = UI()
    UIWindow.show()
    sys.exit(app.exec_())
    
def create_exe():
    '''Creates a direc acces executable file in the user desktop'''
    desktop = os.path.normpath(os.path.expanduser("~/Desktop"))
    exe = shutil.which("dp4plus")
    
    shutil.copy(exe, desktop)
    return 

if __name__=='__main__': 

    main()
