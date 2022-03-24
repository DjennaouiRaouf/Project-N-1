import sys
from PyQt5 import QtCore, QtGui, uic
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication,QWidget,QPushButton, QFileDialog,QMessageBox
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from main import MAIN
uifile_loading = 'loading.ui'
form_loading, base_loading = uic.loadUiType(uifile_loading)
counter = 0
jumper = 10

class LOADING(QMainWindow, form_loading):

#------------------------------------------------------------------------------
    def minimize(self):
        self.showMinimized()

#------------------------------------------------------------------------------
    def __init__(self):
        super(base_loading,self).__init__()
        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.setWindowFlags(flags)
        self.progressBarValue(0)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 120))
        self.circularBg.setGraphicsEffect(self.shadow)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(15)
        self.show()

#------------------------------------------------------------------------------   
    def progress (self):
        global counter
        global jumper
        value = counter

        htmlText = """<p><span style=" font-size:68pt;">{VALUE}</span><span style=" font-size:58pt; vertical-align:super;">%</span></p>"""

        
        newHtml = htmlText.replace("{VALUE}", str(jumper))

        if(value > jumper):
            self.labelPercentage.setText(newHtml)
            jumper += 10

        if value >= 100: value = 1.000
        self.progressBarValue(value)
        if counter > 100:
            self.timer.stop()
            self.close()
            self.main=MAIN()
            self.main.show()

        counter += 0.5
#------------------------------------------------------------------------------  
    def progressBarValue(self, value):

       
        styleSheet = """
        QFrame{
        	border-radius: 150px;
        	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} rgba(85, 170, 255, 255));
        }
        """

        
        progress = (100 - value) / 100.0

        stop_1 = str(progress - 0.001)
        stop_2 = str(progress)
        newStylesheet = styleSheet.replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2)
        self.circularProgress.setStyleSheet(newStylesheet)

#------------------------------------------------------------------------------   

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LOADING()
    sys.exit(app.exec_())


