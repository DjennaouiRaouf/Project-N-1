import sys
from PyQt5 import QtCore, QtGui, uic
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication,QWidget,QPushButton, QFileDialog,QMessageBox
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import sys
import wave    
import numpy as np
import audio_processing as ap



uifile_main = 'main.ui'
form_main, base_main = uic.loadUiType(uifile_main)

class MAIN(QMainWindow, form_main):
    
  

#------------------------------------------------------------------------------
    def home_act(self):
        
        self.home_btn.setStyleSheet("QPushButton { background-color: blue; border:none;}"+self.btn_hps)
        self.rec_btn.setStyleSheet("QPushButton { border:none; }"+self.btn_hps )
        self.adm.setStyleSheet("QPushButton { border:none; }"+self.btn_hps )
        self.display(0)
#------------------------------------------------------------------------------
    def voice_act(self):
        
        self.rec_btn.setStyleSheet("QPushButton { background-color: blue; border:none;}"+self.btn_hps )
        self.home_btn.setStyleSheet("QPushButton { border:none; }"+self.btn_hps )
        self.adm.setStyleSheet("QPushButton { border:none; }"+self.btn_hps )
        self.display(2)

#------------------------------------------------------------------------------
    def start_act(self):
        
        time_limit=self.spin.value()
        ap.record(None, None, time_limit,'test')
        
#------------------------------------------------------------------------------
    def decisiion_taking(self):
        self.answer=ap.start_testing()
        yn=self.answer[0] #yes or no
        uname=self.answer[1]
        if yn=='yes':
            s= uname+' is allowed'
        if yn=='no':
            s= uname+' is not allowed'
        self.deci.setText(s)
#------------------------------------------------------------------------------
    def admininstration(self):
        self.adm.setStyleSheet("QPushButton { background-color: blue; border:none;}"+self.btn_hps )
        self.home_btn.setStyleSheet("QPushButton { border:none; }"+self.btn_hps )
        self.rec_btn.setStyleSheet("QPushButton { border:none; }"+self.btn_hps )
        self.display(1)          
        
#------------------------------------------------------------------------------
    def display(self,i):
        self.stackedWidget.setCurrentIndex(i)
       
#------------------------------------------------------------------------------
    def S_training(self):
        self.nbr_samples=self.spin_3.value()
        user_name=self.un.text()
        permis=self.permi.text()
        time_limit=self.spin_2.value()
        flag='train'
        ap.record(user_name, self.nbr_samples, time_limit,flag) # ajouter au  data set
        ap.start_training(user_name,permis) # créer le model d'un utilisateur 
#------------------------------------------------------------------------------
    def minimize(self):
        self.showMinimized()

#------------------------------------------------------------------------------
    def __init__(self):
       
        self.btn_hps=" QPushButton:hover{background-color:green;} QPushButton:pressed{background-color:green;}"
        super(base_main,self).__init__()
        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.plot_frame=None
        self.nbr_samples=0
        self.answer=None
        self.move(qtRectangle.topLeft())
        self.setWindowFlags(flags)
        self.home_btn.setStyleSheet("QPushButton { background-color: blue; border:none;}"+self.btn_hps)
        self.rec_btn.setStyleSheet("QPushButton { border:none; }"+self.btn_hps )
        self.button_minimize.clicked.connect(self.minimize)
        self.button_close.clicked.connect(self.close)
        self.exit_btn.clicked.connect(self.close)
        self.home_btn.clicked.connect(self.home_act)
        self.rec_btn.clicked.connect(self.voice_act)
        self.training.clicked.connect(self.S_training)
        
        self.testing.clicked.connect(self.decisiion_taking)
        self.adm.clicked.connect(self.admininstration)
        self.frame_left_menu.setMaximumWidth(70)
        self.frame_left_menu.setMinimumWidth(70)
        self.start.clicked.connect(self.start_act)
        self.display(0)
        
        self.show()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MAIN()
    sys.exit(app.exec_())

