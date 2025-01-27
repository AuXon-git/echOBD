#colour palet of blacks and purple (#7622f4)
#hytech fonts

import os
import sys
import threading
import time
import serial
import obd
import cv2

import random

from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QPushButton, QProgressBar, QLabel, QFrame, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QFont, QFontDatabase, QImage, QPixmap, QTransform, QPainter
from PyQt5.QtCore import Qt, QTimer

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

from threading import Thread

os.system('pyuic5 -x EXPERIMENTAL.ui -o EXPERIMENTALui.py')

from EXPERIMENTALui import *


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('echOBD')
        self.setFixedSize(920, 540)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.counter = 0
        self.n = 300 # total instance
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.loading)
        #self.timer.start(15)
        self.timer.start(1)

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.frame = QFrame()
        self.frame.setObjectName('QFramefs')
        layout.addWidget(self.frame)
        self.LabelTitlefs = QLabel(self.frame)
        self.LabelTitlefs.setObjectName('LabelTitlefs')
        # center labels
        self.LabelTitlefs.resize(self.width() - 10, 150)
        self.LabelTitlefs.move(0, 40) # x, y
        self.LabelTitlefs.setText('echOBD')
        self.LabelTitlefs.setAlignment(Qt.AlignCenter)
        self.LabelDescfsription = QLabel(self.frame)
        self.LabelDescfsription.resize(self.width() - 10, 50)
        self.LabelDescfsription.move(0, self.LabelTitlefs.height())
        self.LabelDescfsription.setObjectName('LabelDescfs')
        self.LabelDescfsription.setText('<strong>Checking Connections...</strong>')
        self.LabelDescfsription.setAlignment(Qt.AlignCenter)
        self.progressBar = QProgressBar(self.frame)
        self.progressBar.setObjectName('QProgressBarfs')
        self.progressBar.resize(self.width() - 200 - 10, 50)
        self.progressBar.move(100, self.LabelDescfsription.y() + 130)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setFormat('%p%')
        self.progressBar.setTextVisible(True)
        self.progressBar.setRange(0, self.n)
        self.progressBar.setValue(20)
        self.LabelLoadingfs = QLabel(self.frame)
        self.LabelLoadingfs.resize(self.width() - 10, 50)
        self.LabelLoadingfs.move(0, self.progressBar.y() + 70)
        self.LabelLoadingfs.setObjectName('LabelLoadingfs')
        self.LabelLoadingfs.setAlignment(Qt.AlignCenter)
        self.LabelLoadingfs.setText('beta 0.9.8')
    def loading(self):
        self.progressBar.setValue(self.counter)
        if self.counter == int(self.n * 0.3):
            self.LabelDescfsription.setText('<strong>Loading Assets...</strong>')
        elif self.counter == int(self.n * 0.6):
            self.LabelDescfsription.setText('<strong>Finishing Up...</strong>')
        elif self.counter >= self.n:
            self.timer.stop()
            self.close()
            time.sleep(1)
            self.window = MainWindow()
            self.window.show()
        self.counter += 1


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('echOBD')
        self.show()
        self.showFullScreen()

        self.ui.SELECTmainwindow.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.mainWindow))
        self.ui.SELECTdiagnostics.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.Diagnostics))
        self.ui.SELECTtracktime.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.trackTime))
        self.ui.SELECTfiller.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.Filler))
        self.ui.SELECTsettings.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.Settings))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont("fonts/maven_pro/MavenPro-Regular.ttf")
    # _id = QtGui.QFontDatabase.addApplicationFont("fonts/maven_pro/MavenPro-SemiBold.ttf")
    # print(QtGui.QFontDatabase.applicationFontFamilies(_id))
    app.setStyleSheet('''
        #LabelTitlefs {
            font-family: Maven Pro;
            font-size: 70px;
            color: #7622f4;
        }
        #LabelDescfs {
            font-family: Maven Pro;
            font-size: 25px;
            color: #c2ced1;
        }
        #LabelLoadingfs {
            font-family: Maven Pro;
            font-size: 25px;
            color: #e8e8eb;
        }
        #QFramefs {
            background-image: url('splashscreenrender.png');
            color: rgb(220, 220, 220);
        }
        #QProgressBarfs {
            background-color: #4e4b4b;
            color: rgb(200, 200, 200);
            border-style: none;
            border-radius: 10px;
            text-align: center;
            font-size: 30px;
        }
        #QProgressBarfs::chunk {
            border-radius: 10px;
            background-color: qlineargradient(spread:pad x1:0, x2:1, y1:0.511364, y2:0.523, stop:0 #5619cb, stop:1 #5700ff);
        }
        ''')
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec_())