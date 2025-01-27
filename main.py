# TO FIX:
#       GAUGES SMOOTHLY MOVE BETWEEN NUMBERS NOT JUMP
#       FUEL SUPPRESSION SYSTEM WORKING ON GRAPH
#       AUTOMATIC START ON CHANGE IN SPEED FOR TIMER
#       MAKING SURE FUEL SUPPRESSION SYSTEM WORKS ON NORMAL GAUGES
#       COMPLETELY ERROR CHECK GRAPH
#       COMPLETELY ERROR CHECK GAUGES
#       EVERY TIME THE GRAPH UPDATES THE TIMER FREEZES

import os
import sys
import threading
import time
import serial
import obd
import cv2

from obd import OBDStatus
from datetime import datetime
import random

from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QPushButton, QProgressBar, QLabel, QFrame, QHBoxLayout, \
    QVBoxLayout
from PyQt5.QtGui import QFont, QFontDatabase, QImage, QPixmap, QTransform, QPainter
from PyQt5.QtCore import Qt, QTimer

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import obd2_codes

from threading import Thread

os.system('pyuic5 -x interface.ui -o interface.py')

from interface import *

import obd_datacall as extcon


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('echOBD')
        self.setFixedSize(920, 540)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.counter = 0
        self.n = 300  # total instance
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.loading)
        # self.timer.start(15)
        self.timer.start(10)

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
        self.LabelTitlefs.move(0, 40)  # x, y
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
        self.LabelLoadingfs.setText('Release 1.0.0')

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

        extcon.Timers.__init__(self)

        self.revonoffstatus = False
        self.gearonoffstatus = False
        self.speedonoffstatus = False
        self.boostonoffstatus = False
        self.oilteonoffstatus = False
        self.oilpronoffstatus = False
        self.volonoffstatus = False
        self.tbfonoffstatus = False
        self.fuelpronoffstatus = False
        self.fuelonoffstatus = False
        self.allonoffstatus = False

        ################################################## HIDDEN ######################################################

        self.ui.stt.hide()
        self.ui.stb.hide()
        self.ui.cup.hide()
        self.ui.cdo.hide()
        self.ui.bup.hide()
        self.ui.bdo.hide()
        self.ui.aup.hide()
        self.ui.ado.hide()
        self.ui.pushButton_5.hide()
        self.ui.pushButton_4.hide()
        self.ui.makeplot.hide()
        self.ui.plotsim.hide()

        self.baropre = 0
        self.inmapres = 0
        self.intaketemp = 0
        self.maf = 0
        self.clnttemp = 0
        self.voltage = 8
        selfengineload = 0

        ################################################################################################################

        self.rpmtracker = 0

        self.returns = []

        self.ui.label_8.setText('CURRENT TIME: 00:00:00')

        self.ui.textEdit_6.setText('<COMMAND>')
        self.ui.textEdit_3.setText('NONE')

        self.ui.label_22.setText('Software owned and created by Jaxon Irvine\n2022')

        QtGui.QFontDatabase.addApplicationFont("fonts/archivo/Archivo/Archivo-Light.ttf")

        DUMBFIX = '{ white-space: pre-wrap; }'

        self.ui.ConStatus.setText(
            f'<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\"><html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">p, li {DUMBFIX}</style></head><body style=\" font-family:\'Archivo\'; font-size:18pt; font-weight:400; font-style:normal;\"><p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:15pt;\">CURRENT CONNECTION STATUS: OFFLINE</span></p></body></html>')

        self.ui.textEdit.setText(
            f'<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\"><html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">p, li {DUMBFIX}</style></head><body style=\" font-family:\'Archivo\'; font-size:8pt; font-weight:400; font-style:normal;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11.5pt;\">No current error codes.</span></p></body></html>')
        self.ui.textEdit_2.setText(
            f'<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\"><html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">p, li {DUMBFIX}</style></head><body style=\" font-family:\'Archivo\'; font-size:8pt; font-weight:400; font-style:normal;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11.5pt;\">No current error codes.</span></p></body></html>')
        self.ui.textEdit_4.setText(
            f'<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\"><html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">p, li {DUMBFIX}</style></head><body style=\" font-family:\'Archivo\'; font-size:8pt; font-weight:400; font-style:normal;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11.5pt;\">No current returns.</span></p></body></html>')

        self.ui.textEdit_5.setText(
            f'<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\"><html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">p, li {DUMBFIX}</style></head><body style=\" font-family:\'Archivo\'; font-size:8pt; font-weight:400; font-style:normal;\"><p align=\"left\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt;\">Code Dictionary</span></p></body></html>')
        self.ui.textEdit_5.append('')
        for i in obd2_codes.pcodes:
            code = (str(i) + ' : ' + str(obd2_codes.pcodes[i]))
            self.ui.textEdit_5.append(
                f'<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\"><html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">p, li {DUMBFIX}</style></head><body style=\" font-family:\'Archivo\'; font-size:8pt; font-weight:400; font-style:normal;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">{code}</span></p></body></html>')

        def lightmode():
            self.ui.stackedWidget.setStyleSheet('background-color: #c2c7d2;')
            self.ui.BACKGROUNDMAIN.setStyleSheet('background-color: #c2c7d2;')
            self.ui.frame.setStyleSheet('background-color: #e2e4e9')
            self.ui.plainTextEdit_5.setStyleSheet('background-color: #e2e4e9; border 3px inset; border-color: #cacdd4')
            self.ui.textEdit.setStyleSheet(
                'color: #262626; font-family: Archivo; background-color: #e2e4e9; border 3px inset; border-color: #cacdd4')
            self.ui.textEdit_4.setStyleSheet(
                'color: #262626; font-family: Archivo; background-color: #e2e4e9; border 3px inset; border-color: #cacdd4')
            self.ui.ONOFFCONTROLFRAME.setStyleSheet(
                'background-color: #e2e4e9; border: 3px ridge; border-color: #c2c7d2;')
            self.ui.ONOFFCONTROLFRAME2.setStyleSheet(
                'background-color: #e2e4e9; border: 3px ridge; border-color: #c2c7d2;')
            self.ui.SELECTmainwindow.setStyleSheet('color: #262626; font-family: Archivo; background-color: #ffffff;')
            self.ui.SELECTdiagnostics.setStyleSheet('color: #262626; font-family: Archivo; background-color: #ffffff;')
            self.ui.SELECTtracktime.setStyleSheet('color: #262626; font-family: Archivo; background-color: #ffffff;')
            self.ui.SELECTfiller.setStyleSheet('color: #262626; font-family: Archivo; background-color: #ffffff;')
            self.ui.SELECTsettings.setStyleSheet('color: #262626; font-family: Archivo; background-color: #ffffff;')
            self.ui.ConStatus.setStyleSheet('color: #262626; font-family: Archivo; background-color: #ffffff;')
            self.ui.CurTime.setStyleSheet('color: #262626; font-family: Archivo; background-color: #ffffff;')
            self.ui.mwactive.setStyleSheet('background-color: rgb(12, 182, 0);')
            self.ui.ttactive.setStyleSheet('background-color: rgb(12, 182, 0);')
            self.ui.filactive.setStyleSheet('background-color: rgb(12, 182, 0);')
            self.ui.setactive.setStyleSheet('background-color: rgb(12, 182, 0);')
            self.ui.diagactive.setStyleSheet('background-color: rgb(12, 182, 0);')
            self.ui.SIMS.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13px; background-color: #ffffff;')
            self.ui.obdconnectiontest.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13px; background-color: #ffffff;')
            self.ui.E2.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13px; background-color: #ffffff;')
            self.ui.codeupdater.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13px; background-color: #ffffff;')
            self.ui.graphdisplay.setBackground('#e2e4e9')
            ### THEMES ###
            self.ui.revs.setGaugeTheme(0)
            self.ui.speed.setGaugeTheme(0)
            self.ui.psi.setGaugeTheme(3)
            self.ui.oiltemp.setGaugeTheme(3)
            self.ui.oilpressure.setGaugeTheme(3)
            self.ui.voltage.setGaugeTheme(3)
            self.ui.tbf.setGaugeTheme(3)
            self.ui.fuelpressure.setGaugeTheme(3)
            self.ui.fuel.setGaugeTheme(3)
            self.ui.gear.setGaugeTheme(3)
            ### DIAGNOSTICS PAGE ###
            self.ui.textEdit_5.setStyleSheet('''
                                            #textEdit_5 {
                                                color: #262626;
                                                background-color: #e2e4e9;
                                                border: 3px inset; 
                                                border-color: #cacdd4;
                                            }
                                            QScrollBar:vertical {
                                                border: none;
                                                background: #737373;
                                                width: 14px;
                                                margin: 15px 0 15px 0;
                                                border-radius: 0px;
                                             }
                                            QScrollBar::handle:vertical {	
                                                background-color: #d9d9d9;
                                                min-height: 30px;
                                                border-radius: 0px;
                                            }
                                            QScrollBar::handle:vertical:hover{	
                                                background-color: #737373;
                                            }
                                            QScrollBar::handle:vertical:pressed {	
                                                background-color: #dcdcdc;
                                            }
                                            QScrollBar::sub-line:vertical {
                                                border: none;
                                                background-color: #d9d9d9;
                                                height: 15px;
                                                border-top-left-radius: 0px;
                                                border-top-right-radius: 0px;
                                                subcontrol-position: top;
                                                subcontrol-origin: margin;
                                            }
                                            QScrollBar::sub-line:vertical:hover {	
                                                background-color: #727272;
                                            }
                                            QScrollBar::sub-line:vertical:pressed {	
                                                background-color: #dcdcdc;
                                            }
                                            QScrollBar::add-line:vertical {
                                                border: none;
                                                background-color: #d9d9d9;
                                                height: 15px;
                                                border-bottom-left-radius: 0px;
                                                border-bottom-right-radius: 0px;
                                                subcontrol-position: bottom;
                                                subcontrol-origin: margin;
                                            }
                                            QScrollBar::add-line:vertical:hover {	
                                                background-color: #727272;
                                            }
                                            QScrollBar::add-line:vertical:pressed {	
                                                background-color: #dcdcdc;
                                            }
                                            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                                                background: none;
                                            }
                                            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                                                background: #d2d2d2;
                                            }
                                            ''')
            self.ui.textEdit_3.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 14pt; background-color: #e2e4e9; border: 3px inset; border-color: #cacdd4;')
            self.ui.label.setStyleSheet(
                'padding-left: 7px; border: 3px inset; border-right: 0px solid; border-color: #cacdd4; background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 13.1pt;')
            self.ui.textEdit_6.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13.1pt; background-color: #e2e4e9; border: 3px inset; border-left: 0px solid; border-color: #cacdd4;')
            self.ui.pushButton_3.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13px; background-color: #ffffff;')

            self.ui.label_21.setStyleSheet(
                'color: #262626; font-family: Archivo; background-color: #e2e4e9; border: 0px inset;')
            self.ui.frame_22.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #cacdd4; border 3px inset; border-color: #cacdd4')

            ### GRAPH STYLING ###
            self.ui.updatevalueperline.setStyleSheet('color: #262626; font-family: Archivo; background-color: none;')
            styles = {'color': 'black', 'font-size': '20px'}
            self.ui.graphdisplay.setLabel('left', 'Values (eng load; %, rpm; x1000, speed; kph, fuel; %)', **styles)
            self.ui.graphdisplay.setLabel('bottom', 'Time (seconds)', **styles)
            self.ui.frame_4.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #cacdd4; border 3px inset; border-color: #cacdd4')
            self.ui.textEdit_2.setStyleSheet(
                'color: #262626; font-family: Archivo; background-color: #e2e4e9; border: 0px inset;')
            self.ui.frame_2.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #cacdd4; border 3px inset; border-color: #cacdd4')
            self.ui.CAMERAVIEW.setStyleSheet(
                'color: #262626; font-family: Archivo; background-color: #e2e4e9; border: 0px inset;')
            self.ui.textEdit_7.setStyleSheet(
                'color: #262626; font-family: Archivo; background-color: #e2e4e9; border: 0px inset;')
            self.ui.frame_5.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #cacdd4; border 3px inset; border-color: #cacdd4')
            self.ui.widget_2.setStyleSheet(
                'color: #262626; font-family: Archivo; background-color: #e2e4e9; border: 0px inset;')
            self.ui.label_7.setStyleSheet(
                'color: #262626; font-family: Archivo; background-color: #e2e4e9; border: 0px inset;')
            self.ui.frame_6.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #cacdd4; border 3px inset; border-color: #cacdd4')
            self.ui.label_8.setStyleSheet(
                'color: #262626; font-family: Archivo; background-color: #e2e4e9; border: 0px inset;')
            self.ui.frame_7.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #cacdd4; border 3px inset; border-color: #cacdd4')
            self.ui.label_8.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.frame_8.setStyleSheet(
                'background-color: #e2e4e9; border: 3px inset; border-color: #cacdd4; border 3px inset; border-color: #cacdd4')
            self.ui.label_2.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.frame_9.setStyleSheet(
                'background-color: #e2e4e9; border: 3px inset; border-color: #cacdd4; border 3px inset; border-color: #cacdd4')
            self.ui.line.setStyleSheet('color: #e2e4e9;')
            self.ui.line_3.setStyleSheet('color: #e2e4e9;')
            self.ui.line_4.setStyleSheet('color: #e2e4e9;')
            self.ui.line_5.setStyleSheet('color: #e2e4e9;')
            self.ui.line_6.setStyleSheet('color: #e2e4e9;')
            self.ui.line_7.setStyleSheet('color: #e2e4e9;')
            self.ui.line_17.setStyleSheet('color: #e2e4e9;')
            self.ui.line_20.setStyleSheet('color: #e2e4e9;')
            self.ui.line_21.setStyleSheet('color: #e2e4e9;')
            self.ui.line_22.setStyleSheet('color: #e2e4e9;')
            self.ui.line_23.setStyleSheet('color: #e2e4e9;')
            self.ui.camstartnstop.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13px; background-color: #ffffff;')
            self.ui.updatecam.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13px; background-color: #ffffff;')
            self.ui.camselctor.setStyleSheet(
                'padding-left: 8px; color: #262626; font-family: Archivo; font-size: 13px; background-color: #ffffff;')
            self.ui.tracktimestart.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13px; background-color: #ffffff;')
            self.ui.obdgraphstart.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13px; background-color: #ffffff;')
            self.ui.stopgraph.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13px; background-color: #ffffff;')
            self.ui.clearplot.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13px; background-color: #ffffff;')
            self.ui.automatictimerstart.setStyleSheet(
                'padding-left: 8px; color: #262626; font-family: Archivo; font-size: 13px; background-color: #ffffff; border: 0px solid;')
            self.ui.manualtimerstart.setStyleSheet(
                'padding-left: 8px; color: #262626; font-family: Archivo; font-size: 13px; background-color: #ffffff; border: 0px solid;')

            self.ui.frame_10.setStyleSheet(
                'background-color: #e2e4e9; border: 3px inset; border-color: #cacdd4;')
            self.ui.label_10.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 10pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.frame_11.setStyleSheet(
                'background-color: #e2e4e9; border: 3px inset; border-color: #cacdd4;')
            self.ui.label_11.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 10pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.frame_12.setStyleSheet(
                'background-color: #e2e4e9; border: 3px inset; border-color: #cacdd4;')
            self.ui.label_12.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 10pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            ### SETTINGS ###
            self.ui.frame_13.setStyleSheet(
                'background-color: #e2e4e9; border: 3px inset; border-color: #cacdd4;')
            self.ui.label_9.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 20pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.frame_14.setStyleSheet(
                'background-color: #e2e4e9; border: 3px inset; border-color: #cacdd4;')
            self.ui.label_13.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 20pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.frame_15.setStyleSheet(
                'background-color: #e2e4e9; border: 3px inset; border-color: #cacdd4;')
            self.ui.label_14.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 20pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.frame_16.setStyleSheet(
                'background-color: #e2e4e9; border: 3px inset; border-color: #cacdd4;')
            self.ui.label_15.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 20pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.line_2.setStyleSheet('color: #e2e4e9;')
            self.ui.line_24.setStyleSheet('color: #e2e4e9;')
            self.ui.line_25.setStyleSheet('color: #e2e4e9;')
            self.ui.line_26.setStyleSheet('color: #e2e4e9;')
            self.ui.line_27.setStyleSheet('color: #e2e4e9;')
            self.ui.frame_17.setStyleSheet(
                'background-color: #e2e4e9; border: 3px inset; border-color: #cacdd4;')
            self.ui.frame_18.setStyleSheet(
                'background-color: #e2e4e9; border: 3px inset; border-color: #cacdd4;')
            self.ui.frame_19.setStyleSheet(
                'background-color: #e2e4e9; border: 3px inset; border-color: #cacdd4;')
            self.ui.frame_20.setStyleSheet(
                'background-color: #e2e4e9; border: 3px inset; border-color: #cacdd4;')
            self.ui.frame_21.setStyleSheet(
                'background-color: #e2e4e9; border: 3px inset; border-color: #cacdd4;')

            self.ui.widget.setStyleSheet(
                'border: 0px solid; border-bottom: 3px outset; border-top: 3px outset; border-color: #cacdd4; background-color: none;')
            self.ui.widget_3.setStyleSheet(
                'border: 0px solid; border-bottom: 3px outset; border-top: 3px outset; border-color: #cacdd4; background-color: none;')
            self.ui.widget_4.setStyleSheet(
                'border: 0px solid; border-bottom: 3px outset; border-top: 3px outset; border-color: #cacdd4; background-color: none;')
            self.ui.widget_5.setStyleSheet(
                'border: 0px solid; border-bottom: 3px outset; border-top: 3px outset; border-color: #cacdd4; background-color: none;')
            self.ui.widget_6.setStyleSheet(
                'border: 0px solid; border-bottom: 3px outset; border-top: 3px outset; border-color: #cacdd4; background-color: none;')

            self.ui.label_16.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_2.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_3.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_4.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_5.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_6.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_7.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_8.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_9.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_10.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.label_17.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_11.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_12.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_13.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_14.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_15.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_16.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')

            self.ui.label_18.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_17.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.label_19.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_18.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.label_20.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_19.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid;')

            self.ui.LIGHTORDARK.setStyleSheet(
                'padding-left: 8px; color: #262626; font-family: Archivo; font-size: 13px; background-color: #ffffff;')

            self.ui.pushButton.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13pt; background-color: #ffffff;')
            self.ui.pushButton_2.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13pt; background-color: #ffffff;')
            self.ui.updateprogramthemeBUTTON.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13pt; background-color: #ffffff;')
            self.ui.pushButton_6.setStyleSheet(
                'color: #262626; font-family: Archivo; font-size: 13pt; background-color: #ffffff;')

            self.ui.label_22.setStyleSheet(
                'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 10pt; border: 0px solid; qproperty-alignment: AlignCenter;')

            ### STARTSTOPBUTTONS ###
            if self.revonoffstatus:
                self.ui.revON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: green;')
            else:
                self.ui.revON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: red;')
            if self.gearonoffstatus:
                self.ui.gearON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: green;')
            else:
                self.ui.gearON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: red;')
            if self.speedonoffstatus:
                self.ui.speedON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: green;')
            else:
                self.ui.speedON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: red;')
            if self.boostonoffstatus:
                self.ui.boostON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: green;')
            else:
                self.ui.boostON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: red;')
            if self.oilteonoffstatus:
                self.ui.oilteON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: green;')
            else:
                self.ui.oilteON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: red;')
            if self.oilpronoffstatus:
                self.ui.oilprON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: green;')
            else:
                self.ui.oilprON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: red;')
            if self.volonoffstatus:
                self.ui.volON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: green;')
            else:
                self.ui.volON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: red;')
            if self.tbfonoffstatus:
                self.ui.tbfON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: green;')
            else:
                self.ui.tbfON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: red;')
            if self.fuelpronoffstatus:
                self.ui.fuelprON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: green;')
            else:
                self.ui.fuelprON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: red;')
            if self.fuelonoffstatus:
                self.ui.fuelON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: green;')
            else:
                self.ui.fuelON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: red;')
            if self.fuelonoffstatus:
                self.ui.allON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: green;')
            else:
                self.ui.allON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 13px; '
                    'background-color: #ffffff; border: 2px outset; border-color: red;')

        def darkmode():
            self.ui.stackedWidget.setStyleSheet('background-color: #121212')
            self.ui.BACKGROUNDMAIN.setStyleSheet('background-color: #121212')
            self.ui.frame.setStyleSheet('background-color: #1d1d1d')
            self.ui.plainTextEdit_5.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.textEdit.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.textEdit_4.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.ONOFFCONTROLFRAME.setStyleSheet(
                'background-color: #1b1b1b; border: 3px ridge; border-color: #121212;')
            self.ui.ONOFFCONTROLFRAME2.setStyleSheet(
                'background-color: #1b1b1b; border: 3px ridge; border-color: #121212;')
            self.ui.SELECTmainwindow.setStyleSheet('color: #cdcdcd; font-family: Archivo; background-color: #222222;')
            self.ui.SELECTdiagnostics.setStyleSheet('color: #cdcdcd; font-family: Archivo; background-color: #222222;')
            self.ui.SELECTtracktime.setStyleSheet('color: #cdcdcd; font-family: Archivo; background-color: #222222;')
            self.ui.SELECTfiller.setStyleSheet('color: #cdcdcd; font-family: Archivo; background-color: #222222;')
            self.ui.SELECTsettings.setStyleSheet('color: #cdcdcd; font-family: Archivo; background-color: #222222;')
            self.ui.ConStatus.setStyleSheet('color: #cdcdcd; font-family: Archivo; background-color: #222222;')
            self.ui.CurTime.setStyleSheet('color: #cdcdcd; font-family: Archivo; background-color: #222222;')
            self.ui.mwactive.setStyleSheet('background-color: rgb(165, 0, 0);')
            self.ui.ttactive.setStyleSheet('background-color: rgb(165, 0, 0);')
            self.ui.filactive.setStyleSheet('background-color: rgb(165, 0, 0);')
            self.ui.setactive.setStyleSheet('background-color: rgb(165, 0, 0);')
            self.ui.diagactive.setStyleSheet('background-color: rgb(165, 0, 0);')
            self.ui.SIMS.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 13px; background-color: #222222;')
            self.ui.obdconnectiontest.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 13px; background-color: #222222;')
            self.ui.E2.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 13px; background-color: #222222;')
            self.ui.codeupdater.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 13px; background-color: #222222;')
            self.ui.graphdisplay.setBackground('#121212')
            ### DIAGNOSTICS PAGE ###
            self.ui.textEdit_5.setStyleSheet('''
                                            #textEdit_5 {
                                                color: #cdcdcd; 
                                                background-color: #1d1d1d; 
                                                border: 3px inset; 
                                                border-color: #212121;
                                            }
                                            QScrollBar:vertical {
                                                border: none;
                                                background: #373737;
                                                width: 14px;
                                                margin: 15px 0 15px 0;
                                                border-radius: 0px;
                                             }
                                            QScrollBar::handle:vertical {	
                                                background-color: #272727;
                                                min-height: 30px;
                                                border-radius: 0px;
                                            }
                                            QScrollBar::handle:vertical:hover{	
                                                background-color: #cdcdcd;
                                            }
                                            QScrollBar::handle:vertical:pressed {	
                                                background-color: #373737;
                                            }
                                            QScrollBar::sub-line:vertical {
                                                border: none;
                                                background-color: #373737;
                                                height: 15px;
                                                border-top-left-radius: 0px;
                                                border-top-right-radius: 0px;
                                                subcontrol-position: top;
                                                subcontrol-origin: margin;
                                            }
                                            QScrollBar::sub-line:vertical:hover {	
                                                background-color: #cdcdcd;
                                            }
                                            QScrollBar::sub-line:vertical:pressed {	
                                                background-color: #272727;
                                            }
                                            QScrollBar::add-line:vertical {
                                                border: none;
                                                background-color: #373737;
                                                height: 15px;
                                                border-bottom-left-radius: 0px;
                                                border-bottom-right-radius: 0px;
                                                subcontrol-position: bottom;
                                                subcontrol-origin: margin;
                                            }
                                            QScrollBar::add-line:vertical:hover {	
                                                background-color: #cdcdcd;
                                            }
                                            QScrollBar::add-line:vertical:pressed {	
                                                background-color: #272727;
                                            }
                                            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                                                background: none;
                                            }
                                            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                                                background: #2d2d2d;
                                            }
                                            ''')
            self.ui.textEdit_3.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 14pt; background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.label.setStyleSheet(
                'padding-left: 7px; border: 3px inset; border-right: 0px solid; border-color: #212121; background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 13.1pt;')
            self.ui.textEdit_6.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 12pt; background-color: #1d1d1d; border: 3px inset; border-left: 0px solid; border-color: #212121;')
            self.ui.pushButton_3.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 13px; background-color: #222222;')

            self.ui.label_21.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; background-color: #1d1d1d; border: 0px inset;')
            self.ui.frame_22.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')

            ### GRAPH STYLING ###
            self.ui.updatevalueperline.setStyleSheet('color: #cdcdcd; font-family: Archivo; background-color: none;')
            styles = {'color': 'white', 'font-size': '20px'}
            self.ui.graphdisplay.setLabel('left', 'Values (eng load; %, rpm; x1000, speed; kph, fuel; %)', **styles)
            self.ui.graphdisplay.setLabel('bottom', 'Time (seconds)', **styles)
            self.ui.frame_4.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.textEdit_2.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; background-color: #1d1d1d; border: 0px inset;')
            self.ui.frame_2.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.CAMERAVIEW.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; background-color: #1d1d1d; border: 0px inset;')
            self.ui.textEdit_7.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; background-color: #1d1d1d; border: 0px inset;')
            self.ui.frame_5.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.widget_2.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; background-color: #1d1d1d; border: 0px inset;')
            self.ui.label_7.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; background-color: #1d1d1d; border: 0px inset;')
            self.ui.frame_6.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.label_8.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; background-color: #1d1d1d; border: 0px inset;')
            self.ui.frame_7.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.label_8.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.frame_8.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.label_2.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.frame_9.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.line.setStyleSheet('color: #1d1d1d;')
            self.ui.line_3.setStyleSheet('color: #1d1d1d;')
            self.ui.line_4.setStyleSheet('color: #1d1d1d;')
            self.ui.line_5.setStyleSheet('color: #1d1d1d;')
            self.ui.line_6.setStyleSheet('color: #1d1d1d;')
            self.ui.line_7.setStyleSheet('color: #1d1d1d;')
            self.ui.line_17.setStyleSheet('color: #1d1d1d;')
            self.ui.line_20.setStyleSheet('color: #1d1d1d;')
            self.ui.line_21.setStyleSheet('color: #1d1d1d;')
            self.ui.line_22.setStyleSheet('color: #1d1d1d;')
            self.ui.line_23.setStyleSheet('color: #1d1d1d;')
            self.ui.camstartnstop.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 13px; background-color: #222222;')
            self.ui.updatecam.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 13px; background-color: #222222;')
            self.ui.camselctor.setStyleSheet(
                'padding-left: 8px; color: #cdcdcd; font-family: Archivo; font-size: 13px; background-color: #222222;')
            self.ui.tracktimestart.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 13px; background-color: #222222;')
            self.ui.obdgraphstart.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 13px; background-color: #222222;')
            self.ui.stopgraph.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 13px; background-color: #222222;')
            self.ui.clearplot.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 13px; background-color: #222222;')
            self.ui.automatictimerstart.setStyleSheet(
                'padding-left: 8px; color: #cdcdcd; font-family: Archivo; font-size: 13px; background-color: #222222; border: 0px solid;')
            self.ui.manualtimerstart.setStyleSheet(
                'padding-left: 8px; color: #cdcdcd; font-family: Archivo; font-size: 13px; background-color: #222222; border: 0px solid;')

            self.ui.frame_10.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.label_10.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 10pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.frame_11.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.label_11.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 10pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.frame_12.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.label_12.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 10pt; border: 0px solid; qproperty-alignment: AlignCenter;')

            ### SETTINGS ###
            self.ui.frame_13.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.label_9.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 20pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.frame_14.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.label_13.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 20pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.frame_15.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.label_14.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 20pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.frame_16.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.label_15.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 20pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            self.ui.line_2.setStyleSheet('color: #1d1d1d;')
            self.ui.line_24.setStyleSheet('color: #1d1d1d;')
            self.ui.line_25.setStyleSheet('color: #1d1d1d;')
            self.ui.line_26.setStyleSheet('color: #1d1d1d;')
            self.ui.line_27.setStyleSheet('color: #1d1d1d;')
            self.ui.frame_17.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.frame_18.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.frame_19.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.frame_20.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')
            self.ui.frame_21.setStyleSheet(
                'background-color: #1d1d1d; border: 3px inset; border-color: #212121;')

            self.ui.widget.setStyleSheet(
                'border: 0px solid; border-bottom: 3px outset; border-color: #212121; background-color: none;')
            self.ui.widget_3.setStyleSheet(
                'border: 0px solid; border-bottom: 3px outset; border-color: #212121; background-color: none;')
            self.ui.widget_4.setStyleSheet(
                'border: 0px solid; border-bottom: 3px outset; border-color: #212121; background-color: none;')
            self.ui.widget_5.setStyleSheet(
                'border: 0px solid; border-bottom: 3px outset; border-color: #212121; background-color: none;')
            self.ui.widget_6.setStyleSheet(
                'border: 0px solid; border-bottom: 3px outset; border-color: #212121; background-color: none;')

            self.ui.label_16.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_2.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_3.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_4.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_5.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_6.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_7.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_8.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_9.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_10.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.label_17.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_11.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_12.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_13.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_14.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_15.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_16.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')

            self.ui.label_18.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_17.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.label_19.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_18.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.label_20.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')
            self.ui.radioButton_19.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid;')

            self.ui.LIGHTORDARK.setStyleSheet(
                'padding-left: 8px; color: #cdcdcd; font-family: Archivo; font-size: 13px; background-color: #222222;')

            self.ui.pushButton.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 13pt; background-color: #222222;')
            self.ui.pushButton_2.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 13pt; background-color: #222222;')
            self.ui.updateprogramthemeBUTTON.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 13pt; background-color: #222222;')
            self.ui.pushButton_6.setStyleSheet(
                'color: #cdcdcd; font-family: Archivo; font-size: 13pt; background-color: #222222;')

            self.ui.label_22.setStyleSheet(
                'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 10pt; border: 0px solid; qproperty-alignment: AlignCenter;')

            ### THEMES ###
            self.ui.revs.setGaugeTheme(0)
            self.ui.speed.setGaugeTheme(0)
            self.ui.psi.setGaugeTheme(25)
            self.ui.oiltemp.setGaugeTheme(25)
            self.ui.oilpressure.setGaugeTheme(25)
            self.ui.voltage.setGaugeTheme(25)
            self.ui.tbf.setGaugeTheme(25)
            self.ui.fuelpressure.setGaugeTheme(25)
            self.ui.fuel.setGaugeTheme(25)
            self.ui.gear.setGaugeTheme(25)
            ### STARTSTOPBUTTONS ###
            if self.revonoffstatus:
                self.ui.revON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: green;')
            else:
                self.ui.revON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: red;')
            if self.gearonoffstatus:
                self.ui.gearON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: green;')
            else:
                self.ui.gearON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: red;')
            if self.speedonoffstatus:
                self.ui.speedON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: green;')
            else:
                self.ui.speedON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: red;')
            if self.boostonoffstatus:
                self.ui.boostON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: green;')
            else:
                self.ui.boostON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: red;')
            if self.oilteonoffstatus:
                self.ui.oilteON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: green;')
            else:
                self.ui.oilteON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: red;')
            if self.oilpronoffstatus:
                self.ui.oilprON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: green;')
            else:
                self.ui.oilprON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: red;')
            if self.volonoffstatus:
                self.ui.volON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: green;')
            else:
                self.ui.volON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: red;')
            if self.tbfonoffstatus:
                self.ui.tbfON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: green;')
            else:
                self.ui.tbfON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: red;')
            if self.fuelpronoffstatus:
                self.ui.fuelprON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: green;')
            else:
                self.ui.fuelprON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: red;')
            if self.fuelonoffstatus:
                self.ui.fuelON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: green;')
            else:
                self.ui.fuelON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: red;')
            if self.fuelonoffstatus:
                self.ui.allON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: green;')
            else:
                self.ui.allON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                    'background-color: #222222; border: 2px outset; border-color: red;')

        def updateprogramtheme():
            if self.ui.LIGHTORDARK.currentIndex() == 0:
                darkmode()
            elif self.ui.LIGHTORDARK.currentIndex() == 1:
                lightmode()

        updateprogramtheme()
        self.ui.updateprogramthemeBUTTON.clicked.connect(lambda: updateprogramtheme())

        def clock():
            now = datetime.now()
            CURRENTHOUR = now.strftime("%H")
            CURRENTMINUTE = now.strftime("%M")
            dumbfix = '{ white-space: pre-wrap; }'
            if int(CURRENTHOUR) <= 11:
                AMPM = 'AM'
                self.ui.CurTime.setText(
                    f'<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\"><html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">p, li {dumbfix}</style></head><body style=\" font-family:\'Archivo\'; font-size:18pt; font-weight:400; font-style:normal;\"><p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:15pt;\">{CURRENTHOUR}:{CURRENTMINUTE} {AMPM}</span></p></body></html>')
            else:
                AMPM = 'PM'
                CURRENTHOUR = int(CURRENTHOUR) - 12
                if CURRENTHOUR == 00:
                    CURRENTHOUR = '12'
                elif CURRENTHOUR < 10:
                    CURRENTHOUR = f'0{str(CURRENTHOUR)}'
                self.ui.CurTime.setText(
                    f'<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\"><html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">p, li {dumbfix}</style></head><body style=\" font-family:\'Archivo\'; font-size:18pt; font-weight:400; font-style:normal;\"><p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:15pt;\">{CURRENTHOUR}:{CURRENTMINUTE} {AMPM}</span></p></body></html>')

        clock()
        self.clockcount = QtCore.QTimer()
        self.clockcount.timeout.connect(clock)
        self.clockcount.setInterval(15000)
        self.clockcount.start()

        self.ui.mwactive.show()
        self.ui.ttactive.hide()
        self.ui.filactive.hide()
        self.ui.setactive.hide()
        self.ui.diagactive.hide()

        def smw():
            self.ui.mwactive.show()
            self.ui.ttactive.hide()
            self.ui.filactive.hide()
            self.ui.setactive.hide()
            self.ui.diagactive.hide()
            self.ui.stackedWidget.setCurrentWidget(self.ui.mainWindow)

        def sdi():
            self.ui.mwactive.hide()
            self.ui.ttactive.hide()
            self.ui.filactive.hide()
            self.ui.setactive.hide()
            self.ui.diagactive.show()
            self.ui.stackedWidget.setCurrentWidget(self.ui.Diagnostics)

        def strti():
            self.ui.mwactive.hide()
            self.ui.ttactive.show()
            self.ui.filactive.hide()
            self.ui.setactive.hide()
            self.ui.diagactive.hide()
            self.ui.stackedWidget.setCurrentWidget(self.ui.trackTime)

        def sfi():
            self.ui.mwactive.hide()
            self.ui.ttactive.hide()
            self.ui.filactive.show()
            self.ui.setactive.hide()
            self.ui.diagactive.hide()
            self.ui.stackedWidget.setCurrentWidget(self.ui.Filler)

        def sse():
            self.ui.mwactive.hide()
            self.ui.ttactive.hide()
            self.ui.filactive.hide()
            self.ui.setactive.show()
            self.ui.diagactive.hide()
            self.ui.stackedWidget.setCurrentWidget(self.ui.Settings)

        self.ui.SELECTmainwindow.clicked.connect(lambda: smw())
        self.ui.SELECTdiagnostics.clicked.connect(lambda: sdi())
        self.ui.SELECTtracktime.clicked.connect(lambda: strti())
        self.ui.SELECTfiller.clicked.connect(lambda: sfi())
        self.ui.SELECTsettings.clicked.connect(lambda: sse())

        self.textboxitemlist = []

        def updateconsoletextbox():
            if self.returns == []:
                return
            else:
                settext = []
                DUMBFIX = '{ white-space: pre-wrap; }'
                for i in self.returns[-11:-1]:
                    settext.append(
                        f'<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\"><html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">p, li {DUMBFIX}</style></head><body style=\" font-family:\'Archivo\'; font-size:8pt; font-weight:400; font-style:normal;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11.5pt;\">{i}</span></p></body></html>')
                settext = '\n'.join(settext)
                self.ui.textEdit_4.setText(settext)

        # self.consoletotext = QtCore.QTimer()
        # self.consoletotext.setInterval(5000)
        # self.consoletotext.timeout.connect(updateconsoletextbox)
        # self.consoletotext.start()

        ################################################################################################################
        #                                          SERIAL INITIALIZATION                                               #
        ################################################################################################################

        self.ui.obdconnectiontest.clicked.connect(lambda: MainWindow.makeconnection(self))

        ################################################################################################################
        #                                            FUNCTION LIST START                                               #
        ################################################################################################################

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: viewCam())
        self.ui.camstartnstop.clicked.connect(lambda: controlTimer())
        self.ui.updatecam.clicked.connect(lambda: camSelect())
        self.currentCamera = -2
        self.ui.textEdit_7.show()
        self.cap = cv2.VideoCapture(self.currentCamera, cv2.CAP_DSHOW)

        # self.cap.set(3, 1280)
        # self.cap.set(4, 720)
        def camSelect():
            def cs():
                index = self.ui.camselctor.currentIndex()
                if index == 0:
                    self.currentCamera = -2
                elif index == 1:
                    self.currentCamera = -1
                elif index == 2:
                    self.currentCamera = 0
                elif index == 3:
                    self.currentCamera = 1
                elif index == 4:
                    self.currentCamera = 2
                elif index == 5:
                    self.currentCamera = 3
                elif index == 6:
                    self.currentCamera = 4
                elif index == 7:
                    self.currentCamera = 5
                if self.timer.isActive():
                    controlTimer()
                    self.cap = cv2.VideoCapture(self.currentCamera)
                    controlTimer()
                elif not self.timer.isActive():
                    self.cap = cv2.VideoCapture(self.currentCamera)

            # t = threading.Thread(target=lambda: cs())
            # t.start()
            cs()

        def viewCam():
            def vc():
                try:
                    ret, image = self.cap.read()
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    height, width, channel = image.shape
                    step = channel * width
                    qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
                    self.ui.CAMERAVIEW.setPixmap(QPixmap.fromImage(qImg))
                except:
                    if self.currentCamera == -2:
                        self.ui.CAMERAVIEW.setText("error on cam 1")
                    elif self.currentCamera == -1:
                        self.ui.CAMERAVIEW.setText("error on cam 2")
                    elif self.currentCamera == 0:
                        self.ui.CAMERAVIEW.setText("error on cam 3")
                    elif self.currentCamera == 1:
                        self.ui.CAMERAVIEW.setText("error on cam 4")
                    elif self.currentCamera == 2:
                        self.ui.CAMERAVIEW.setText("error on cam 5")
                    elif self.currentCamera == 3:
                        self.ui.CAMERAVIEW.setText("error on cam 6")
                    elif self.currentCamera == 4:
                        self.ui.CAMERAVIEW.setText("error on cam 7")
                    elif self.currentCamera == 5:
                        self.ui.CAMERAVIEW.setText("error on cam 8")
                    else:
                        self.ui.CAMERAVIEW.setText("error")
                    return

            # t = threading.Thread(target=lambda:vc())
            # t.start()
            vc()

        def controlTimer():
            if not self.timer.isActive():
                self.ui.textEdit_7.hide()
                self.timer.start(20)
                self.ui.camstartnstop.setText("Stop")
            else:
                self.timer.stop()
                self.cap.release()
                self.ui.textEdit_7.show()
                self.ui.camstartnstop.setText("Start")
            # t = threading.Thread(target=lambda: ct())
            # t.start()

        ################################################################################################################

        def exitprogram():
            def exitprocess():
                if self.revpowerstatus:
                    revonoff()
                    time.sleep(0.3)
                if self.oiltepowerstatus:
                    oilteSTATUSon()
                    time.sleep(0.3)
                if self.tbfpowerstatus:
                    tbfSTATUSon()
                    time.sleep(0.3)
                if self.boostpowerstatus:
                    boostSTATUSon()
                    time.sleep(0.3)
                if self.gearpowerstatus:
                    gearSTATUSon()
                    time.sleep(0.3)
                if self.speedpowerstatus:
                    speedSTATUSon()
                    time.sleep(0.3)
                if self.oilprpowerstatus:
                    oilprSTATUSon()
                    time.sleep(0.3)
                if self.fuelprpowerstatus:
                    fuelprSTATUSon()
                    time.sleep(0.3)
                if self.volpowerstatus:
                    volSTATUSon()
                    time.sleep(0.3)
                if self.fuelpowerstatus:
                    fuelSTATUSon()
                    time.sleep(0.3)
                os._exit(1)

            t = threading.Thread(target=exitprocess)
            t.start()

        ################################################################################################################
        #                                           OBD CONTROL LIST START                                             #
        ################################################################################################################

        # def calfour(rcv): # not sure how to do yet ||| # Calculating the decimal value of 4 byte hexadecimal numbers
        #     return

        # def serialrpm():
        #     # def flushserial():
        #     #     self.ser.flushInput()
        #     #     self.ser.flushOutput()
        #     # def caltwo(rcv):
        #     #     r = rcv.split(b'\r', 1)
        #     #     v = r[1]
        #     #     v = v[6:-3]
        #     #     a = int(v[0:2], 16)
        #     #     b = int(v[3:5], 16)
        #     #     return {'A': a, 'B': b}
        #     # flushserial()
        #     # self.ser.write(b"010C\r")
        #     # rcv = self.ser.readline()
        #     # r = caltwo(rcv)
        #     # a = r['A']; b = r['B']
        #     # rpm = (a * 256 + b) / 4
        #     res = con.query(obd.commands.RPM)
        #     rpm = float(str(res.value).replace(' revolutions_per_minute', ''))
        #     self.ui.revs.updateValue(rpm)
        #
        # def serialspeed():
        #     # def flushserial():
        #     #     self.ser.flushInput()
        #     #     self.ser.flushOutput()
        #     # def calone(rcv):
        #     #     r = rcv.split(b'\r', 1)
        #     #     v = r[1]
        #     #     v = v[6:-3]
        #     #     vspeed = int(v, 16)
        #     #     return vspeed
        #     # flushserial()
        #     # self.ser.write(b"010D\r")
        #     # rcv = self.ser.readline()
        #     # speed = calone(rcv)
        #     # self.ui.revs.updateValue(speed)
        #     res = con.query(obd.commands.SPEED)
        #     speed = float(str(res.value).replace(' kph', ''))
        #     self.ui.speed.updateValue(speed)
        #
        # def serialfuel():
        #     # def flushserial():
        #     #     self.ser.flushInput()
        #     #     self.ser.flushOutput()
        #     # def calone(rcv):
        #     #     r = rcv.split(b'\r', 1)
        #     #     v = r[1]
        #     #     v = v[6:-3]
        #     #     vspeed = int(v, 16)
        #     #     return vspeed
        #     # flushserial()
        #     # self.ser.write(b"012F\r")
        #     # rcv = self.ser.readline()
        #     # fuel = calone(rcv)
        #     # fuel = (100/255)*fuel
        #     # print(fuel)
        #     # self.ui.fuel.updateValue(fuel)
        #     res = self.con.query(obd.commands.FUEL_LEVEL)
        #     fuel = print(res.value)
        #
        # def serialbaropre():
        #     # def flushserial():
        #     #     self.ser.flushInput()
        #     #     self.ser.flushOutput()
        #     # def calone(rcv):
        #     #     r = rcv.split(b'\r', 1)
        #     #     v = r[1]
        #     #     v = v[6:-3]
        #     #     vspeed = int(v, 16)
        #     #     return vspeed
        #     # flushserial()
        #     # self.ser.write(b"015C\r")
        #     # rcv = self.ser.readline()
        #     # oiltemp = calone(rcv)
        #     # oiltemp = oiltemp-40
        #     # self.ui.oiltemp.updateValue(oiltemp)
        #     res = self.con.query(obd.commands.OIL_TEMP)
        #     oiltemp = print(res.value)
        #
        # def serialvoltage():
        #     def flushserial():
        #         self.ser.flushInput()
        #         self.ser.flushOutput()
        #     flushserial()
        #     self.ser.write(bytes('atrv\r\n', encoding='utf-8'))
        #     rcv = self.ser.read(999).decode('utf-8')
        #     rcvv = []
        #     for i in rcv:
        #         rcvv.append(i)
        #     rcvvv = str(rcvv[5] + rcvv[6] + rcvv[7] + rcvv[8])[0:]
        #     #print(int(float(rcvvv)))
        #     self.ui.voltage.updateValue(float(rcvvv))
        #     #time.sleep(3)

        # def temprun():
        #     while True:
        # serialrpm()
        # serialbaropre()
        # serialinmapres()
        # serialmaf()
        # serialintaketemp()
        # serialclnttemp()
        # serialengineload()
        # serialspeed()
        # serialvoltage()
        # serialfuel()
        # self.con = obd.OBD('COM1')
        # t = threading.Thread(target=lambda: temprun())
        # t.start()
        # self.gaugego = QtCore.QTimer()
        # self.gaugego.setInterval(50)
        # self.gaugego.timeout.connect(temprun)
        # self.gaugego.start()

        ### CURRENT EDITION ###
        # self.activecons = []

        # def running():
        #     def letsago():
        #         if 1 in self.activecons:
        #             serialrpm()
        #         if 2 in self.activecons:
        #             serialspeed()
        #         if 3 in self.activecons:
        #             serialvoltage()
        #         if 4 in self.activecons:
        #             serialfuel()
        #     self.gaugego = QtCore.QTimer()
        #     self.gaugego.setInterval(50)
        #     self.gaugego.timeout.connect(letsago)
        #     self.gaugego.start()
        #
        # def tmeptemptemp():
        #     serialrpm()
        #     serialspeed()
        #     time.sleep(1)
        # self.gaugego = QtCore.QTimer()
        # self.gaugego.setInterval(50)
        # self.gaugego.timeout.connect(tmeptemptemp)
        # self.gaugego.start()

        ### EXPERIMENTAL EDITION ###
        # def running():
        #     self.gaugerpm = QtCore.QTimer()
        #     self.gaugerpm.setInterval(500)
        #     self.gaugerpm.timeout.connect(serialrpm)
        #     self.gaugerpm.start()
        #     self.gaugespeed = QtCore.QTimer()
        #     self.gaugespeed.setInterval(500)
        #     self.gaugespeed.timeout.connect(serialspeed)
        #     self.gaugespeed.start()
        #     self.gaugevoltage = QtCore.QTimer()
        #     self.gaugevoltage.setInterval(500)
        #     self.gaugevoltage.timeout.connect(serialvoltage)
        #     self.gaugevoltage.start()
        #     self.gaugefuel = QtCore.QTimer()
        #     self.gaugefuel.setInterval(500)
        #     self.gaugefuel.timeout.connect(serialfuel)
        #     self.gaugefuel.start()

        # def stoprunning():
        #     self.gaugego.stop()

        ################################################################################################################
        #                                           OBD CONTROL LIST FINISH                                            #
        ################################################################################################################

        ################################################################################################################
        #                                            FUNCTION LIST FINISH                                              #
        ################################################################################################################

        ###  GRAPHS  ###
        # self.ui.graphdisplay.setBackground((100,50,255))
        # self.ui.graphdisplay.enableAutoRange(axis=None, enable=True, x=None, y=None)
        self.editgraph = pg.GraphicsLayoutWidget()
        # pg.viewBox
        self.ui.graphdisplay.setXRange(0, 60, padding=0)
        self.ui.graphdisplay.setYRange(0, 243, padding=0)
        self.ui.graphdisplay.setTitle("GRAPH DATA", color="r", size="20pt")
        self.ui.graphdisplay.showGrid(x=True, y=True)
        self.ui.graphdisplay.addLegend()
        legend = pg.LegendItem()
        self.ui.graphdisplay.enableMouse(False)

        # self.ui.graphdisplay.useOpenGL(True)
        # pw1.enableAutoRange(axis='y')
        # pw1.setMouseEnabled(x=True, y=False)
        # pyqtgraph.setConfigOption('leftButtonPan', False)

        def plot(x, y, plotname, color, symbol, symbolsize):
            pen = pg.mkPen(color=color, width=2.5)
            plotreturn = self.ui.graphdisplay.plot(x, y, name=plotname, pen=pen, symbol=symbol, symbolSize=symbolsize)
            return plotreturn

        def clearplot():
            self.ui.graphdisplay.clear()
            self.ui.updatevalueperline.setText('')
            _translate = QtCore.QCoreApplication.translate
            # self.ui.tracktime.setHtml(_translate("MainWindow",
            #                                      "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
            #                                      "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
            #                                      "p, li { white-space: pre-wrap; }\n"
            #                                      "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
            #                                      f"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">CURRENT TIME: 00:00:00</span></p></body></html>"))
            self.ui.label_8.setText('CURRENT TIME: 00:00:00')
            if self.ui.LIGHTORDARK.currentIndex() == 0:
                self.ui.label_8.setStyleSheet(
                    'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            elif self.ui.LIGHTORDARK.currentIndex() == 1:
                self.ui.label_8.setStyleSheet(
                    'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid; qproperty-alignment: AlignCenter;')

        def plotsetup():
            plot([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [30, 32, 34, 32, 33, 31, 29, 32, 35, 45], 'RPM', 'r', '+', 0)
            plot([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [50, 35, 44, 22, 38, 32, 27, 38, 32, 44], 'SPEED', 'g', '+', 20)

        def plotsim():
            def updatevalues():
                self.ui.updatevalueperline.setText(f'rpm: {self.y[-1]}\nspeed: {self.t[-1]}')

            def update_plot_data():
                self.x = self.x[1:]
                self.x.append(self.x[-1] + 1)
                self.y = self.y[1:]
                self.y.append(random.randint(0, 50))
                self.data_line.setData(self.x, self.y)
                updatevalues()

            self.ui.graphdisplay.setXRange(0, 50, padding=0)
            self.ui.graphdisplay.setYRange(0, 50, padding=0)
            self.x = list(range(50))
            self.y = [random.randint(0, 50) for _ in range(50)]
            # pen = pg.mkPen(color='r', width=2.5)
            self.data_line = plot(self.x, self.y, 'RPM', 'r', '+', 10)

            def update_plot_data2():
                self.z = self.z[1:]
                self.z.append(self.z[-1] + 1)
                self.t = self.t[1:]
                self.t.append(random.randint(0, 50))
                self.data_line2.setData(self.z, self.t)
                updatevalues()

            self.z = list(range(50))
            self.t = [random.randint(0, 50) for _ in range(50)]
            # pen2 = pg.mkPen(color='g', width=2.5)
            self.data_line2 = plot(self.x, self.t, 'SPEED', 'g', '+', 10)
            # pg.ViewBox
            # self.data_line.enableAutoRange(axis='y')
            # self.data_line.setMouseEnabled(x=True, y=False)
            # self.ui.graphdisplay.plot.getViewBox()
            self.othert = QtCore.QTimer()
            self.othert.setInterval(1000)
            self.othert.timeout.connect(update_plot_data)
            self.othert.start()
            self.othert2 = QtCore.QTimer()
            self.othert2.setInterval(1000)
            self.othert2.timeout.connect(update_plot_data2)
            self.othert2.start()
            # self.othert3 = QtCore.QTimer()
            # self.othert3.setInterval(1000)
            # self.othert3.timeout.connect(updatevalues)
            # self.othert3.start()

        self.ui.plotsim.clicked.connect(lambda: plotsim())
        self.ui.makeplot.clicked.connect(lambda: plotsetup())
        self.ui.clearplot.clicked.connect(lambda: clearplot())

        def serialrpmgraph():
            try:
                res = self.con.query(obd.commands.RPM)
                rpm = float(str(res.value).replace(' revolutions_per_minute', ''))
                rpm = int(str("{:.0f}".format(rpm)))
                return rpm
            except:
                return self.serialrpmgraphreturn
        def serialspeedgraph():
            try:
                res = self.con.query(obd.commands.SPEED)
                speed = float(str(res.value).replace(' kph', ''))
                speed = int(str("{:.0f}".format(speed)))
                return speed
            except:
                return self.serialspeedgraphreturn
        # def serialstartupfuel():
        #     try:
        #         res = self.con.query(obd.commands.FUEL_LEVEL)
        #         fuel = int(str(res.value).replace(' percent', ''))
        #         return fuel
        def serialfuelgraph():
            try:
                return 63
                # res = self.con.query(obd.commands.FUEL_LEVEL)
                # fuel = int(str(res.value).replace(' percent', ''))
                # return fuel
            # speed = self.serialspeedgraphreturn
            # checkcurrentlevel = self.forlastcheck
            # if speed != 0:
            #     if fuel < (checkcurrentlevel - 5):
            #         return checkcurrentlevel
            #     elif fuel > (checkcurrentlevel + 5):
            #         return checkcurrentlevel
            #     else:
            #         return fuel
            # else:
            #     return fuel
            except:
                return 63
        def serialengloadgraph():
            try:
                res = self.con.query(obd.commands.ENGINE_LOAD)
                engload = float(str(res.value).replace(' percent', ''))
                engload = int(str("{:.0f}".format(engload)))
                return engload
            except:
                return self.serialengloadgraphreturn

        def startobdplotting():
            clearplot()
            ### SET GRAPH RULES ###
            self.ui.graphdisplay.setXRange(0, 60, padding=0)
            self.ui.graphdisplay.setYRange(0, 243, padding=0)
            ### SET OTHER RULES ###
            self.serialengloadgraphreturn = 0
            self.serialrpmgraphreturn = 0
            self.serialspeedgraphreturn = 0
            self.serialfuelgraphreturn = 0
            self.lastcallyes = False
            ### DATA DISPLAY UPDATER ###
            def updatevalues():self.ui.updatevalueperline.setText(f' eng load: {self.serialengloadgraphreturn}\n rpm: {self.serialrpmgraphreturn}\n speed: {self.serialspeedgraphreturn}\n fuel: {self.serialfuelgraphreturn}')

            # def updatevalues():
            #     self.ui.updatevalueperline.setText(
            #         f' eng load: {serialengloadgraph()}\n rpm: {serialrpmgraph()}\n speed: {serialspeedgraph()}')

            ### UPDATE DATA FOR FUNCTIONS ###
            def data_update_call():
                # while self.datacallcontinue:
                if self.lastcallyes:
                    self.serialrpmgraphreturn = serialrpmgraph()
                    self.serialspeedgraphreturn = serialspeedgraph()
                    self.serialfuelgraphreturn = serialfuelgraph()
                    self.serialengloadgraphreturn = serialengloadgraph()
                    self.lastcallyes = False
                    return # IMPORTANT OR FUCKS WITH TIMER
                elif not self.lastcallyes:
                    self.lastcallyes = True
                    return # IMPORTANT OR FUCKS WITH TIMER
                    #time.sleep(0.5)

            ### SET FUNCTIONS FOR DATA UPDATES ###
            def update_rev_plot_data():
                self.rev_x = self.rev_x[1:]
                self.rev_x.append(self.rev_x[-1] + 1)
                self.rev_y = self.rev_y[1:]
                self.rev_y.append(self.serialrpmgraphreturn / 33.333333333)
                self.rev_data_line.setData(self.rev_x, self.rev_y)
                self.ui.graphdisplay.setXRange(min(self.rev_x), max(self.rev_x))
                self.ui.graphdisplay.setYRange(0, 240)
                updatevalues()
            def update_speed_plot_data():
                self.speed_x = self.speed_x[1:]
                self.speed_x.append(self.speed_x[-1] + 1)
                self.speed_y = self.speed_y[1:]
                self.speed_y.append(self.serialspeedgraphreturn)
                self.speed_data_line.setData(self.speed_x, self.speed_y)
                updatevalues()
            def update_fuel_plot_data():
                self.fuel_x = self.fuel_x[1:]
                self.fuel_x.append(self.fuel_x[-1] + 1)
                self.fuel_y = self.fuel_y[1:]
                self.fuel_y.append(self.serialfuelgraphreturn * 2.4)
                self.fuel_data_line.setData(self.fuel_x, self.fuel_y)
                updatevalues()
            def update_engload_plot_data():
                self.engload_x = self.engload_x[1:]
                self.engload_x.append(self.engload_x[-1] + 1)
                self.engload_y = self.engload_y[1:]
                self.engload_y.append(self.serialengloadgraphreturn * 2.4)
                self.engload_data_line.setData(self.engload_x, self.engload_y)
                updatevalues()
            ### SET RANGES AND PLOTS FOR DATA LINES ###
            self.engload_x = list(range(50))
            self.engload_y = list(range(50))
            if self.ui.LIGHTORDARK.currentIndex() == 0:
                self.engload_data_line = plot(self.engload_x, self.engload_y, 'ENG LOAD', 'w', 's', 7.5)
            elif self.ui.LIGHTORDARK.currentIndex() == 1:
                self.engload_data_line = plot(self.engload_x, self.engload_y, 'ENG LOAD', 'black', 's', 7.5)
            self.rev_x = list(range(50))
            self.rev_y = list(range(50))
            self.rev_data_line = plot(self.rev_x, self.rev_y, 'RPM', 'r', '+', 7.5)
            self.speed_x = list(range(50))
            self.speed_y = list(range(50))
            self.speed_data_line = plot(self.speed_x, self.speed_y, 'SPEED', 'g', 'x', 7.5)
            self.fuel_x = list(range(50))
            self.fuel_y = list(range(50))
            self.fuel_data_line = plot(self.fuel_x, self.fuel_y, 'FUEL', 'b', 'o', 7.5)
            ### SET TIMERS TO UPDATE DATA ###
            self.revtimer = QtCore.QTimer()
            self.revtimer.setInterval(1000)
            self.revtimer.timeout.connect(update_rev_plot_data)
            self.revtimer.start()
            self.speedtimer = QtCore.QTimer()
            self.speedtimer.setInterval(1000)
            self.speedtimer.timeout.connect(update_speed_plot_data)
            self.speedtimer.start()
            self.fueltimer = QtCore.QTimer()
            self.fueltimer.setInterval(1000)
            self.fueltimer.timeout.connect(update_fuel_plot_data)
            self.fueltimer.start()
            self.engloadtimer = QtCore.QTimer()
            self.engloadtimer.setInterval(1000)
            self.engloadtimer.timeout.connect(update_engload_plot_data)
            self.engloadtimer.start()
            self.datacalltimer = QtCore.QTimer()
            self.datacalltimer.setInterval(500)
            self.datacalltimer.timeout.connect(data_update_call)
            self.datacalltimer.start()
            self.datacallcontinue = True
            # datacalltimer = threading.Thread(target=lambda: data_update_call())
            # datacalltimer.start()

        def stopobdplot():
            self.revtimer.stop()
            self.speedtimer.stop()
            self.fueltimer.stop()
            self.engloadtimer.stop()
            self.datacallcontinue = False
            self.lastcallyes = False
            # self.datacalltimer.stop()

        self.ui.obdgraphstart.clicked.connect(lambda: startobdplotting())
        self.ui.stopgraph.clicked.connect(lambda: stopobdplot())

        # def plot(hour, temperature):
        #     pen = pg.mkPen(color=(255, 0, 0), width=5)
        #     self.ui.graphdisplay.plot(hour, temperature, name='RPM', pen=pen, symbol='+', symbolSize=20, symbolBrush='b')
        #
        # plot([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [30, 32, 34, 32, 33, 31, 29, 32, 35, 45])

        ###  STEERING WHEEL  ###

        self.rrr = 15

        def stt():
            self.ui.STEERINGwheel.clear()
            pixmap = QtGui.QPixmap(QImage('mx5ndsteeringwheel.png'))
            self.rrr += 15
            transform = QtGui.QTransform().rotate(self.rrr)
            pixmap = pixmap.transformed(transform, QtCore.Qt.SmoothTransformation)
            self.ui.STEERINGwheel.setPixmap(pixmap)
            self.ui.STEERINGwheel.setAlignment(QtCore.Qt.AlignCenter)

        def stb():
            self.ui.STEERINGwheel.clear()
            pixmap = QtGui.QPixmap(QImage('mx5ndsteeringwheel.png'))
            self.rrr -= 15
            transform = QtGui.QTransform().rotate(self.rrr)
            pixmap = pixmap.transformed(transform, QtCore.Qt.SmoothTransformation)
            self.ui.STEERINGwheel.setPixmap(pixmap)
            self.ui.STEERINGwheel.setAlignment(QtCore.Qt.AlignCenter)

        self.ui.stt.clicked.connect(lambda: stt())
        self.ui.stb.clicked.connect(lambda: stb())

        # self.ui.clutchpos.setFormat("")
        # update = self.ui.clutchpos.setValue(100)

        def cup():
            update = self.ui.clutchpos.value()
            update += 1
            self.ui.clutchpos.setValue(update)

        def cdo():
            update = self.ui.clutchpos.value()
            update -= 1
            self.ui.clutchpos.setValue(update)

        self.ui.cup.clicked.connect(lambda: cup())
        self.ui.cdo.clicked.connect(lambda: cdo())

        def bup():
            update = self.ui.brakepos.value()
            update += 1
            self.ui.brakepos.setValue(update)

        def bdo():
            update = self.ui.brakepos.value()
            update -= 1
            self.ui.brakepos.setValue(update)

        self.ui.bup.clicked.connect(lambda: bup())
        self.ui.bdo.clicked.connect(lambda: bdo())

        def aup():
            update = self.ui.acceleratorpos.value()
            update += 1
            self.ui.acceleratorpos.setValue(update)

        def ado():
            update = self.ui.acceleratorpos.value()
            update -= 1
            self.ui.acceleratorpos.setValue(update)

        self.ui.aup.clicked.connect(lambda: aup())
        self.ui.ado.clicked.connect(lambda: ado())

        self.tominresetvalue = 0
        self.elapsedminutes = 0
        self.finalreturn = 'CURRENT TIME: 00:00:00'

        def updatetracktimeinrealtime():
            _translate = QtCore.QCoreApplication.translate
            # self.ui.tracktime.setHtml(_translate("MainWindow",
            #                                      "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
            #                                      "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
            #                                      "p, li { white-space: pre-wrap; }\n"
            #                                      "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
            #                                      f"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">{self.finalreturn}</span></p></body></html>"))
            self.ui.label_8.setText(self.finalreturn)
            if self.ui.LIGHTORDARK.currentIndex() == 0:
                self.ui.label_8.setStyleSheet(
                    'background-color: #1d1d1d; color: #cdcdcd; font-family: Archivo; font-size: 14pt; border: 0px solid; qproperty-alignment: AlignCenter;')
            elif self.ui.LIGHTORDARK.currentIndex() == 1:
                self.ui.label_8.setStyleSheet(
                    'background-color: #e2e4e9; color: #262626; font-family: Archivo; font-size: 14pt; border: 0px solid; qproperty-alignment: AlignCenter;')

        updatetracktimeinrealtime()

        def manualtracktimer():
            def start():
                self.ui.tracktimestart.setText("STOP TIMER")
                self.begin = time.time()
                while self.stopwatchgo:
                    self.end = time.time()
                    self.elapsedseconds = self.end - self.begin
                    self.elapsedmilliseconds = (round(self.elapsedseconds * 100) - (int(self.elapsedseconds) * 100))
                    if int(self.elapsedmilliseconds) <= 9:
                        self.elapsedmilliseconds = f'0{self.elapsedmilliseconds}'
                    if int(self.elapsedmilliseconds) == 100:
                        self.elapsedmilliseconds = '00'
                    if (int(self.elapsedseconds) - self.tominresetvalue) <= 9:
                        self.elapsedseconds = f'0{int(self.elapsedseconds) - self.tominresetvalue}'
                    if (int(self.elapsedseconds) - self.tominresetvalue) >= 10:
                        self.elapsedseconds = int(self.elapsedseconds - self.tominresetvalue)
                    if (int(self.elapsedseconds) - self.tominresetvalue) == 60:
                        self.tominresetvalue += 60
                        self.elapsedminutes += 1
                    if self.elapsedminutes <= 9:
                        self.fminr = f'0{self.elapsedminutes}'
                    if self.elapsedminutes >= 10:
                        self.fminr = self.elapsedminutes
                    self.finalreturn = str(
                        f'CURRENT TIME: {self.fminr}:{self.elapsedseconds}:{self.elapsedmilliseconds}')
                    # print(self.finalreturn)
                    time.sleep(0.01)

            if self.stopwatchgo:
                self.ui.tracktimestart.setText("START TIMER")
                stopobdplot()
                self._update_timer.stop()
                self.stopwatchgo = False
            else:
                self.stopwatchgo = True
                startobdplotting()
                self._update_timer = QtCore.QTimer()
                self._update_timer.timeout.connect(updatetracktimeinrealtime)
                self._update_timer.start(10)
                t = threading.Thread(target=lambda: start())
                t.start()

        def switchedofffortimer():
            self.allpowerstatus = False
            self.allonoffstatus = False
            self.allupdatepowerstatus = False
            if self.revonoffstatus:
                revonoff()
            if self.gearonoffstatus:
                gearSTATUSon()
            if self.speedonoffstatus:
                speedSTATUSon()
            if self.boostonoffstatus:
                boostSTATUSon()
            if self.oilteonoffstatus:
                oilteSTATUSon()
            if self.oilpronoffstatus:
                oilprSTATUSon()
            if self.volonoffstatus:
                volSTATUSon()
            if self.tbfonoffstatus:
                tbfSTATUSon()
            if self.fuelpronoffstatus:
                fuelprSTATUSon()
            if self.fuelonoffstatus:
                fuelSTATUSon()
            if self.ui.LIGHTORDARK.currentIndex() == 0:
                self.ui.allON.setStyleSheet(
                    'color: #cdcdcd; font-family: Archivo; font-size: 12px; '
                    'background-color: #222222; border: 2px outset; border-color: red;')
            elif self.ui.LIGHTORDARK.currentIndex() == 1:
                self.ui.allON.setStyleSheet(
                    'color: #262626; font-family: Archivo; font-size: 12px; '
                    'background-color: #ffffff; border: 2px outset; border-color: red;')

        def autotracktimer():
            def start():
                check = self.serialspeedgraphreturn
                self.ui.tracktimestart.setText("WAITING")
                while check == 0 and self.stopwatchgo:
                    check = self.serialspeedgraphreturn
                    time.sleep(0.1)
                if self.stopwatchgo:
                    self.ui.tracktimestart.setText("STOP TIMER")
                self.begin = time.time()
                while self.stopwatchgo:
                    self.end = time.time()
                    self.elapsedseconds = self.end - self.begin
                    self.elapsedmilliseconds = (round(self.elapsedseconds * 100) - (int(self.elapsedseconds) * 100))
                    if int(self.elapsedmilliseconds) <= 9:
                        self.elapsedmilliseconds = f'0{self.elapsedmilliseconds}'
                    if int(self.elapsedmilliseconds) == 100:
                        self.elapsedmilliseconds = '00'
                    if (int(self.elapsedseconds) - self.tominresetvalue) <= 9:
                        self.elapsedseconds = f'0{int(self.elapsedseconds) - self.tominresetvalue}'
                    if (int(self.elapsedseconds) - self.tominresetvalue) >= 10:
                        self.elapsedseconds = int(self.elapsedseconds - self.tominresetvalue)
                    if (int(self.elapsedseconds) - self.tominresetvalue) == 60:
                        self.tominresetvalue += 60
                        self.elapsedminutes += 1
                    if self.elapsedminutes <= 9:
                        self.fminr = f'0{self.elapsedminutes}'
                    if self.elapsedminutes >= 10:
                        self.fminr = self.elapsedminutes
                    self.finalreturn = str(
                        f'CURRENT TIME: {self.fminr}:{self.elapsedseconds}:{self.elapsedmilliseconds}')
                    # print(self.finalreturn)
                    time.sleep(0.01)

            if self.stopwatchgo:
                self.ui.tracktimestart.setText("START TIMER")
                stopobdplot()
                self._update_timer.stop()
                self.stopwatchgo = False
            else:
                self.stopwatchgo = True
                startobdplotting()
                self._update_timer = QtCore.QTimer()
                self._update_timer.timeout.connect(updatetracktimeinrealtime)
                self._update_timer.start(10)
                t = threading.Thread(target=lambda: start())
                t.start()

        self.currentModeSelected = 'auto'

        def automaticselected():
            self.currentModeSelected = 'auto'

            # self.returns.append('switched to auto')
            # print('switched to auto')

        def manualselected():
            self.currentModeSelected = 'manual'
            # self.returns.append('switched to manual')
            # print('switched to manual')

        self.ui.automatictimerstart.clicked.connect(automaticselected)
        self.ui.manualtimerstart.clicked.connect(manualselected)

        def trackstartmode():
            if self.currentModeSelected == 'auto':
                # print('automatic start')
                # self.returns.append('automatic start')
                switchedofffortimer()
                autotracktimer()
            elif self.currentModeSelected == 'manual':
                # print('manual start')
                # self.returns.append('manual start')
                switchedofffortimer()
                manualtracktimer()

        self.stopwatchgo = False
        self.ui.tracktimestart.clicked.connect(lambda: trackstartmode())

        ################################################################################################################

        # ### TEXT LOCKS ###
        # self.ui.GearNAME.setReadOnly(True)
        # self.ui.GearVNAME.setReadOnly(True)

        def startup():
            time.sleep(0.5)
            MainWindow.begin(self)

        startup = threading.Thread(target=startup)
        startup.start()

        ### BUTTON CONTROLLERS ###
        self.ui.E2.clicked.connect(lambda: exitprogram())

        ### GAUGEUPDATE ###
        # cant do until obd link arrives in mail

        ### FONT INIT ###
        QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(__file__), 'fonts/ds_digital/DS-DIGIB.TTF'))

        ### OTHER ###
        # self.ui.fuel.setDisplayValueColor(34, 255, 0, 255)
        # self.ui.fuel.setScaleValueColor(34, 255, 0, 255)
        # self.ui.revs.setEnableBarGraph(False)
        # self.ui.revs.setEnableCenterPoint(False)

        ### FONTS ###
        self.ui.revs.setValueFontFamily('DS-Digital')
        self.ui.revs.setScaleFontFamily('DS-Digital')
        self.ui.speed.setValueFontFamily('DS-Digital')
        self.ui.speed.setScaleFontFamily('DS-Digital')
        self.ui.psi.setValueFontFamily('DS-Digital')
        self.ui.psi.setScaleFontFamily('DS-Digital')
        self.ui.oiltemp.setValueFontFamily('DS-Digital')
        self.ui.oiltemp.setScaleFontFamily('DS-Digital')
        self.ui.oilpressure.setValueFontFamily('DS-Digital')
        self.ui.oilpressure.setScaleFontFamily('DS-Digital')
        self.ui.voltage.setValueFontFamily('DS-Digital')
        self.ui.voltage.setScaleFontFamily('DS-Digital')
        self.ui.tbf.setValueFontFamily('DS-Digital')
        self.ui.tbf.setScaleFontFamily('DS-Digital')
        self.ui.fuelpressure.setValueFontFamily('DS-Digital')
        self.ui.fuelpressure.setScaleFontFamily('DS-Digital')
        self.ui.fuel.setValueFontFamily('DS-Digital')
        self.ui.fuel.setScaleFontFamily('DS-Digital')
        self.ui.gear.setValueFontFamily('DS-Digital')
        self.ui.gear.setScaleFontFamily('DS-Digital')

        ### NEEDLE ###
        self.ui.revs.setNeedleColor(255, 0, 0)
        self.ui.speed.setNeedleColor(255, 0, 0)
        self.ui.psi.setNeedleColor(255, 0, 0)
        self.ui.oiltemp.setNeedleColor(255, 0, 0)
        self.ui.oilpressure.setNeedleColor(255, 0, 0)
        self.ui.voltage.setNeedleColor(255, 0, 0)
        self.ui.tbf.setNeedleColor(255, 0, 0)
        self.ui.fuelpressure.setNeedleColor(255, 0, 0)
        self.ui.fuel.setNeedleColor(255, 0, 0)
        self.ui.gear.setNeedleColor(255, 0, 0)

        ### NEEDLE C DISABLE ###
        self.ui.revs.setMouseTracking(False)
        self.ui.speed.setMouseTracking(False)
        self.ui.psi.setMouseTracking(False)
        self.ui.oiltemp.setMouseTracking(False)
        self.ui.oilpressure.setMouseTracking(False)
        self.ui.voltage.setMouseTracking(False)
        self.ui.tbf.setMouseTracking(False)
        self.ui.fuelpressure.setMouseTracking(False)
        self.ui.fuel.setMouseTracking(False)
        self.ui.gear.setMouseTracking(False)

        ### BAR GRAPHS ###
        self.ui.revs.enableBarGraph = False
        self.ui.speed.enableBarGraph = False
        self.ui.psi.enableBarGraph = False
        self.ui.oiltemp.enableBarGraph = False
        self.ui.oilpressure.enableBarGraph = False
        self.ui.voltage.enableBarGraph = False
        self.ui.tbf.enableBarGraph = False
        self.ui.fuelpressure.enableBarGraph = False
        self.ui.fuel.enableBarGraph = False
        self.ui.gear.enableBarGraph = False

        ### UNITS ###
        self.ui.revs.units = ''
        self.ui.speed.units = ''
        self.ui.psi.units = ''
        self.ui.oiltemp.units = ''
        self.ui.oilpressure.units = ''
        self.ui.voltage.units = ''
        self.ui.tbf.units = ''
        self.ui.fuelpressure.units = ''
        self.ui.fuel.units = ''
        self.ui.gear.units = ''

        ### REVS ###
        self.ui.revs.units = 'x1000'
        # self.ui.revs.setEnableGaugeName(True)
        # self.ui.revs.gname = 'REVS'
        self.ui.revs.setMaxNMinValueFontFamily(8, 0)
        self.ui.revs.setVaddony(30)
        self.ui.revs.setCustomUnitPosY(-10)
        self.ui.revs.setCustomUnitPosX(62.5)
        self.ui.revs.maxValue = 8000
        self.ui.revs.minValue = 0
        self.ui.revs.scalaCount = 8
        self.ui.revs.value = 0

        ### SPEED ###
        self.ui.speed.units = 'km/h'
        # self.ui.speed.setEnableGaugeName(True)
        # self.ui.speed.gname = 'SPEED'
        self.ui.speed.setMaxNMinValueFontFamily(240, 0)
        self.ui.speed.setVaddony(30)
        self.ui.speed.setCustomUnitPosY(-10)
        self.ui.speed.setCustomUnitPosX(62.5)
        self.ui.speed.maxValue = 240
        self.ui.speed.minValue = 0
        self.ui.speed.scalaCount = 12
        self.ui.speed.value = 0

        ### PSI ###
        self.ui.psi.units = '°C'
        self.ui.psi.setEnableGaugeName(True)
        self.ui.psi.gname = 'CLNT\nTEMP'
        self.ui.psi.setEnableScalePolygon(False)
        self.ui.psi.SETsupercustomvaluefontsizebecausejaxonistoolazytodoitoftheexisitingadjuster(27.5)
        self.ui.psi.setScaleStartAngle(90)
        self.ui.psi.setDrawScaleStartAngle(90)
        self.ui.psi.setTotalScaleAngleSize(270)
        self.ui.psi.setCustomgPosX(31)
        self.ui.psi.setCustomgPosY(15)
        self.ui.psi.setCustomUnitPosX(-11)
        self.ui.psi.setCustomUnitPosY(70)
        self.ui.psi.setVaddonx(12)
        self.ui.psi.setVaddony(38)
        self.ui.psi.setScalePolygonColor(color1='red', color2='orange', color3='yellow')
        self.ui.psi.setFineScaleColor(color='red')
        self.ui.psi.setMaxNMinValueFontFamily(150, 50)
        self.ui.psi.maxValue = 150
        self.ui.psi.minValue = 50
        self.ui.psi.scalaCount = 10

        ### OIL TEMP ###
        self.ui.oiltemp.units = 'kPa'
        self.ui.oiltemp.setEnableGaugeName(True)
        self.ui.oiltemp.gname = 'BARO\nPRES'
        self.ui.oiltemp.setEnableScalePolygon(False)
        self.ui.oiltemp.SETsupercustomvaluefontsizebecausejaxonistoolazytodoitoftheexisitingadjuster(27.5)
        self.ui.oiltemp.setScaleStartAngle(90)
        self.ui.oiltemp.setDrawScaleStartAngle(90)
        self.ui.oiltemp.setTotalScaleAngleSize(270)
        self.ui.oiltemp.setScalePolygonColor(color1='red', color2='orange', color3='yellow')
        self.ui.oiltemp.setFineScaleColor(color='red')
        self.ui.oiltemp.setMaxNMinValueFontFamily(150, 0)
        self.ui.oiltemp.setCustomgPosX(27)
        self.ui.oiltemp.setCustomgPosY(15)
        self.ui.oiltemp.setCustomUnitPosX(-10)
        self.ui.oiltemp.setCustomUnitPosY(70)
        self.ui.oiltemp.setVaddonx(12)
        self.ui.oiltemp.setVaddony(38)
        self.ui.oiltemp.maxValue = 150
        self.ui.oiltemp.minValue = 0
        self.ui.oiltemp.scalaCount = 15
        self.ui.oiltemp.value = 50

        ### OIL PRESSURE ###
        self.ui.oilpressure.units = 'kPa'
        self.ui.oilpressure.setEnableGaugeName(True)
        self.ui.oilpressure.gname = 'IN-MF\nPRES '
        self.ui.oilpressure.setEnableScalePolygon(False)
        self.ui.oilpressure.SETsupercustomvaluefontsizebecausejaxonistoolazytodoitoftheexisitingadjuster(27.5)
        self.ui.oilpressure.setScaleStartAngle(90)
        self.ui.oilpressure.setDrawScaleStartAngle(90)
        self.ui.oilpressure.setTotalScaleAngleSize(270)
        self.ui.oilpressure.setCustomgPosX(27)
        self.ui.oilpressure.setCustomgPosY(15)
        self.ui.oilpressure.setCustomUnitPosX(-16)
        self.ui.oilpressure.setCustomUnitPosY(70)
        self.ui.oilpressure.setVaddonx(12)
        self.ui.oilpressure.setVaddony(38)
        self.ui.oilpressure.setScalePolygonColor(color1='red', color2='orange', color3='yellow')
        self.ui.oilpressure.setFineScaleColor(color='red')
        self.ui.oilpressure.setMaxNMinValueFontFamily(100, 0)
        self.ui.oilpressure.maxValue = 100
        self.ui.oilpressure.minValue = 0
        self.ui.oilpressure.scalaCount = 5
        self.ui.oilpressure.value = 0

        ### VOLTAGE ###
        self.ui.voltage.units = 'Volts'
        self.ui.voltage.setEnableGaugeName(True)
        self.ui.voltage.gname = ' VOLT'
        self.ui.voltage.setEnableScalePolygon(False)
        self.ui.voltage.setCustomDecStatus(True)
        self.ui.voltage.SETsupercustomvaluefontsizebecausejaxonistoolazytodoitoftheexisitingadjuster(20)
        self.ui.voltage.setScaleStartAngle(90)
        self.ui.voltage.setDrawScaleStartAngle(90)
        self.ui.voltage.setTotalScaleAngleSize(270)
        self.ui.voltage.setCustomgPosX(59)
        self.ui.voltage.setCustomgPosY(16)
        self.ui.voltage.setCustomUnitPosX(-25)
        self.ui.voltage.setCustomUnitPosY(70)
        self.ui.voltage.setVaddonx(30)
        self.ui.voltage.setVaddony(30)
        self.ui.voltage.setScalePolygonColor(color1='red', color2='orange', color3='yellow')
        self.ui.voltage.setFineScaleColor(color='red')
        self.ui.voltage.setMaxNMinValueFontFamily(18, 8)
        self.ui.voltage.maxValue = 18
        self.ui.voltage.minValue = 8
        self.ui.voltage.scalaCount = 10
        self.ui.voltage.value = 8

        ### TBF ###
        self.ui.tbf.units = '°C'
        self.ui.tbf.setEnableGaugeName(True)
        self.ui.tbf.gname = 'INTK\nTEMP'
        self.ui.tbf.setEnableScalePolygon(False)
        self.ui.tbf.SETsupercustomvaluefontsizebecausejaxonistoolazytodoitoftheexisitingadjuster(27.5)
        self.ui.tbf.setScaleStartAngle(90)
        self.ui.tbf.setDrawScaleStartAngle(70)
        self.ui.tbf.setTotalScaleAngleSize(270)
        self.ui.tbf.setCustomgPosX(31)
        self.ui.tbf.setCustomgPosY(15)
        self.ui.tbf.setCustomUnitPosX(-11)
        self.ui.tbf.setCustomUnitPosY(70)
        self.ui.tbf.setVaddonx(12)
        self.ui.tbf.setVaddony(38)
        self.ui.tbf.setScalePolygonColor(color1='red', color2='orange', color3='yellow')
        self.ui.tbf.setFineScaleColor(color='red')
        self.ui.tbf.setMaxNMinValueFontFamily(150, 0)
        self.ui.tbf.maxValue = 150
        self.ui.tbf.minValue = 0
        self.ui.tbf.scalaCount = 15
        self.ui.tbf.value = 50

        ### FUEL PRESSURE ###
        self.ui.fuelpressure.units = 'g/s'
        self.ui.fuelpressure.setEnableGaugeName(True)
        self.ui.fuelpressure.setEnableScalePolygon(False)
        self.ui.fuelpressure.gname = 'MAF'
        # self.ui.fuelpressure.setCustomDecStatus(True)
        # self.ui.fuelpressure.SETsupercustomvaluefontsizebecausejaxonistoolazytodoitoftheexisitingadjuster(20)
        self.ui.fuelpressure.SETsupercustomvaluefontsizebecausejaxonistoolazytodoitoftheexisitingadjuster(27.5)
        self.ui.fuelpressure.setScaleStartAngle(90)
        self.ui.fuelpressure.setDrawScaleStartAngle(90)
        self.ui.fuelpressure.setTotalScaleAngleSize(270)
        self.ui.fuelpressure.setCustomgPosX(69)
        self.ui.fuelpressure.setCustomgPosY(16)
        # self.ui.fuelpressure.setCustomUnitPosX(-16)
        self.ui.fuelpressure.setCustomUnitPosX(-11)
        self.ui.fuelpressure.setCustomUnitPosY(70)
        self.ui.fuelpressure.setVaddonx(30)
        self.ui.fuelpressure.setVaddony(30)
        self.ui.fuelpressure.setScalePolygonColor(color1='red', color2='orange', color3='yellow')
        self.ui.fuelpressure.setFineScaleColor(color='red')
        self.ui.fuelpressure.setMaxNMinValueFontFamily(655, 0)
        self.ui.fuelpressure.maxValue = 655
        self.ui.fuelpressure.minValue = 0
        self.ui.fuelpressure.scalaCount = 10
        self.ui.fuelpressure.value = 0

        ### FUEL ###
        self.ui.fuel.setScalePolygonColor(color1='red')
        self.ui.fuel.setEnableValueText(False)
        self.ui.fuel.setEnableGaugeName(True)
        self.ui.fuel.gname = ' FUEL'
        self.ui.fuel.setEnableScalePolygon(False)
        self.ui.fuel.setMaxNMinValueFontFamily(8008135, 0)
        self.ui.fuel.maxValue = 0
        self.ui.fuel.minValue = -100
        self.ui.fuel.scalaCount = 1
        self.ui.fuel.setCustomgPosX(-76)
        self.ui.fuel.setCustomgPosY(120)
        self.ui.fuel.setScaleStartAngle(39)
        self.ui.fuel.setDrawScaleStartAngle(39)
        self.ui.fuel.setTotalScaleAngleSize(100)
        self.ui.fuel.value = 0

        ### GEAR ###
        self.ui.gear.units = '%'
        self.ui.gear.setScalePolygonColor(color1='red')
        self.ui.gear.setEnableValueText(True)
        self.ui.gear.setEnableGaugeName(True)
        self.ui.gear.gname = 'ENG\nLOAD'
        self.ui.gear.setEnableScalePolygon(False)
        self.ui.gear.SETsupercustomvaluefontsizebecausejaxonistoolazytodoitoftheexisitingadjuster(27.5)
        self.ui.gear.setScaleStartAngle(90)
        self.ui.gear.setDrawScaleStartAngle(90)
        self.ui.gear.setTotalScaleAngleSize(270)
        self.ui.gear.setCustomgPosX(33)
        self.ui.gear.setCustomgPosY(16)
        self.ui.gear.setCustomUnitPosX(-11)
        self.ui.gear.setCustomUnitPosY(70)
        self.ui.gear.setVaddonx(12)
        self.ui.gear.setVaddony(38)
        # self.ui.gear.setEnableCenterPoint(False)
        self.ui.gear.setScalePolygonColor(color1='red', color2='orange', color3='yellow')
        self.ui.gear.setFineScaleColor(color='red')
        self.ui.gear.setMaxNMinValueFontFamily(100, 0)
        self.ui.gear.maxValue = 100
        self.ui.gear.minValue = 0
        self.ui.gear.scalaCount = 5
        self.ui.gear.value = 0

        # self.ui.gear.setEnableNeedlePolygon(False)
        # self.ui.gear.setEnableBarGraph(False)
        # self.ui.gear.setEnableBigScaleGrid(False)
        # self.ui.gear.setEnableFineScaleGrid(False)
        # self.ui.gear.setEnableScalePolygon(False)
        # self.ui.gear.setEnableScaleText(False)
        # self.ui.gear.setScalePolygonColor(color1='white', color2='white', color3='white')
        # self.ui.gear.setFineScaleColor(color='white')
        # self.ui.gear.setCustomGaugeTheme(color1='white', color2='white', color3='white')
        # self.ui.gear.maxValue = 6
        # self.ui.gear.minValue = -1
        # self.ui.gear.scalaCount = 7

        ################## TESTING ####################

        ### CURRENTLY IN ANOTHER FUNCTION ###

        def revonoff():
            if not self.revonoffstatus:
                if self.revpowerstatus == False:
                    self.revpowerstatus = True

                    def revs():
                        # self.ui.revSTATUS.setStyleSheet("background-color:rgb(255, 140, 39);")
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.revON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: rgb(255,140,39);')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.revON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: rgb(14,42,199);')
                        self.ui.revs.updateValue(0)
                        # tkr = self.ui.revs.value
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr += 133.333333
                        #     self.ui.revs.updateValue(tkr)
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr -= 133.333333
                        #     self.ui.revs.updateValue(tkr)
                        time.sleep(0.5)
                        self.rpmupdatepowerstatus = True
                        self.revonoffstatus = True
                        # self.ui.revSTATUS.setStyleSheet("background-color:rgb(0, 255, 0);")
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.revON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: green;')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.revON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: green;')

                    t = threading.Thread(target=revs)
                    t.start()
                    # self.returns.append(extcon.Timers.rpmgaugetimerstart(self))
                    extcon.Timers.rpmgaugetimerstart(self)
                else:
                    return
            else:
                if self.revpowerstatus:
                    self.revpowerstatus = False
                    self.rpmupdatepowerstatus = False
                    # self.returns.append(extcon.Timers.rpmgaugetimerstop(self))
                    extcon.Timers.rpmgaugetimerstop(self)
                    # self.ui.revSTATUS.setStyleSheet("background-color:rgb(255, 0, 0);")
                    if self.ui.LIGHTORDARK.currentIndex() == 0:
                        self.ui.revON.setStyleSheet(
                            'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                            'background-color: #222222; border: 2px outset; border-color: red;')
                    elif self.ui.LIGHTORDARK.currentIndex() == 1:
                        self.ui.revON.setStyleSheet(
                            'color: #262626; font-family: Archivo; font-size: 13px; '
                            'background-color: #ffffff; border: 2px outset; border-color: red;')
                    self.revonoffstatus = False
                else:
                    return

        self.revpowerstatus = False
        self.rpmupdatepowerstatus = False
        self.ui.revON.clicked.connect(lambda: revonoff())

        def gearSTATUSon():
            if not self.gearonoffstatus:
                if self.gearpowerstatus == False:
                    self.gearpowerstatus = True

                    def gear():
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.gearON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: rgb(255,140,39);')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.gearON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: rgb(14,42,199);')
                        self.ui.gear.updateValue(0)
                        # tkr = self.ui.gear.value
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr += 1.66666667
                        #     self.ui.gear.updateValue(tkr)
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr -= 1.66666667
                        #     self.ui.gear.updateValue(tkr)
                        time.sleep(0.5)
                        self.engineloadupdatepowerstatus = True
                        self.gearonoffstatus = True
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.gearON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: green;')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.gearON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: green;')

                    t = threading.Thread(target=gear)
                    t.start()
                    # self.returns.append(extcon.Timers.engineloadgaugetimerstart(self))
                    extcon.Timers.engineloadgaugetimerstart(self)
                else:
                    return
            else:
                if self.gearpowerstatus:
                    self.gearpowerstatus = False
                    self.gearonoffstatus = False
                    self.engineloadupdatepowerstatus = False
                    # self.returns.append(extcon.Timers.engineloadgaugetimerstop(self))
                    extcon.Timers.engineloadgaugetimerstop(self)
                    if self.ui.LIGHTORDARK.currentIndex() == 0:
                        self.ui.gearON.setStyleSheet(
                            'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                            'background-color: #222222; border: 2px outset; border-color: red;')
                    elif self.ui.LIGHTORDARK.currentIndex() == 1:
                        self.ui.gearON.setStyleSheet(
                            'color: #262626; font-family: Archivo; font-size: 13px; '
                            'background-color: #ffffff; border: 2px outset; border-color: red;')
                else:
                    return

        self.gearpowerstatus = False
        self.engineloadupdatepowerstatus = False
        self.ui.gearON.clicked.connect(lambda: gearSTATUSon())

        def speedSTATUSon():
            if not self.speedonoffstatus:
                if self.speedpowerstatus == False:
                    self.speedpowerstatus = True

                    def speed():
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.speedON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: rgb(255,140,39);')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.speedON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: rgb(14,42,199);')
                        self.ui.speed.updateValue(0)
                        # tkr = self.ui.speed.value
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr += 4
                        #     self.ui.speed.updateValue(tkr)
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr -= 4
                        #     self.ui.speed.updateValue(tkr)
                        time.sleep(0.5)
                        self.speedupdatepowerstatus = True
                        self.speedonoffstatus = True
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.speedON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: green;')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.speedON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: green;')

                    t = threading.Thread(target=speed)
                    t.start()
                    # self.returns.append(extcon.Timers.speedgaugetimerstart(self))
                    extcon.Timers.speedgaugetimerstart(self)
                else:
                    return
            else:
                if self.speedpowerstatus:
                    self.speedpowerstatus = False
                    self.speedonoffstatus = False
                    self.speedupdatepowerstatus = False
                    # self.returns.append(extcon.Timers.speedgaugetimerstop(self))
                    extcon.Timers.speedgaugetimerstop(self)
                    if self.ui.LIGHTORDARK.currentIndex() == 0:
                        self.ui.speedON.setStyleSheet(
                            'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                            'background-color: #222222; border: 2px outset; border-color: red;')
                    elif self.ui.LIGHTORDARK.currentIndex() == 1:
                        self.ui.speedON.setStyleSheet(
                            'color: #262626; font-family: Archivo; font-size: 13px; '
                            'background-color: #ffffff; border: 2px outset; border-color: red;')
                else:
                    return

        self.speedpowerstatus = False
        self.speedupdatepowerstatus = False
        self.ui.speedON.clicked.connect(lambda: speedSTATUSon())

        def boostSTATUSon():
            if not self.boostonoffstatus:
                if self.boostpowerstatus == False:
                    self.boostpowerstatus = True

                    def boost():
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.boostON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: rgb(255,140,39);')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.boostON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: rgb(14,42,199);')
                        self.ui.psi.updateValue(-15)
                        # tkr = self.ui.psi.value
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr += 1.66666667
                        #     self.ui.psi.updateValue(tkr)
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr -= 1.66666667
                        #     self.ui.psi.updateValue(tkr)
                        time.sleep(0.5)
                        self.clnttempupdatepowerstatus = True
                        self.boostonoffstatus = True
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.boostON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: green;')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.boostON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: green;')

                    t = threading.Thread(target=boost)
                    t.start()
                    # self.returns.append(extcon.Timers.clnttempgaugetimerstart(self))
                    extcon.Timers.clnttempgaugetimerstart(self)
                else:
                    return
            else:
                if self.boostpowerstatus:
                    self.boostpowerstatus = False
                    self.boostonoffstatus = False
                    self.clnttempupdatepowerstatus = False
                    # self.returns.append(extcon.Timers.clnttempgaugetimerstop(self))
                    extcon.Timers.clnttempgaugetimerstop(self)
                    if self.ui.LIGHTORDARK.currentIndex() == 0:
                        self.ui.boostON.setStyleSheet(
                            'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                            'background-color: #222222; border: 2px outset; border-color: red;')
                    elif self.ui.LIGHTORDARK.currentIndex() == 1:
                        self.ui.boostON.setStyleSheet(
                            'color: #262626; font-family: Archivo; font-size: 13px; '
                            'background-color: #ffffff; border: 2px outset; border-color: red;')
                else:
                    return

        self.boostpowerstatus = False
        self.clnttempupdatepowerstatus = False
        self.ui.boostON.clicked.connect(lambda: boostSTATUSon())

        def oilteSTATUSon():
            if not self.oilteonoffstatus:
                if self.oiltepowerstatus == False:
                    self.oiltepowerstatus = True

                    def oilte():
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.oilteON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: rgb(255,140,39);')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.oilteON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: rgb(14,42,199);')
                        self.ui.oiltemp.updateValue(-40)
                        # tkr = self.ui.oiltemp.value
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr += 2.5
                        #     self.ui.oiltemp.updateValue(tkr)
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr -= 2.5
                        #     self.ui.oiltemp.updateValue(tkr)
                        time.sleep(0.5)
                        self.baropreupdatepowerstatus = True
                        self.oilteonoffstatus = True
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.oilteON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: green;')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.oilteON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: green;')

                    t = threading.Thread(target=oilte)
                    t.start()
                    # self.returns.append(extcon.Timers.baropregaugetimerstart(self))
                    extcon.Timers.baropregaugetimerstart(self)
                else:
                    return
            else:
                if self.oiltepowerstatus:
                    self.oiltepowerstatus = False
                    self.oilteonoffstatus = False
                    self.baropreupdatepowerstatus = False
                    # self.returns.append(extcon.Timers.baropregaugetimerstop(self))
                    extcon.Timers.baropregaugetimerstop(self)
                    if self.ui.LIGHTORDARK.currentIndex() == 0:
                        self.ui.oilteON.setStyleSheet(
                            'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                            'background-color: #222222; border: 2px outset; border-color: red;')
                    elif self.ui.LIGHTORDARK.currentIndex() == 1:
                        self.ui.oilteON.setStyleSheet(
                            'color: #262626; font-family: Archivo; font-size: 13px; '
                            'background-color: #ffffff; border: 2px outset; border-color: red;')
                else:
                    return

        self.oiltepowerstatus = False
        self.baropreupdatepowerstatus = False
        self.ui.oilteON.clicked.connect(lambda: oilteSTATUSon())

        def oilprSTATUSon():
            if not self.oilpronoffstatus:
                if self.oilprpowerstatus == False:
                    self.oilprpowerstatus = True

                    def oilpr():
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.oilprON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: rgb(255,140,39);')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.oilprON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: rgb(14,42,199);')
                        self.ui.oilpressure.updateValue(0)
                        # tkr = self.ui.oilpressure.value
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr += 1.66666667
                        #     self.ui.oilpressure.updateValue(tkr)
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr -= 1.66666667
                        #     self.ui.oilpressure.updateValue(tkr)
                        time.sleep(0.5)
                        self.inmaupdatepowerstatus = True
                        self.oilpronoffstatus = True
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.oilprON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: green;')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.oilprON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: green;')

                    t = threading.Thread(target=oilpr)
                    t.start()
                    # self.returns.append(extcon.Timers.inmapresgaugetimerstart(self))
                    extcon.Timers.inmapresgaugetimerstart(self)
                else:
                    return
            else:
                if self.oilprpowerstatus:
                    self.oilprpowerstatus = False
                    self.oilpronoffstatus = False
                    self.inmaupdatepowerstatus = False
                    # self.returns.append(extcon.Timers.inmapresgaugetimerstop(self))
                    extcon.Timers.inmapresgaugetimerstop(self)
                    if self.ui.LIGHTORDARK.currentIndex() == 0:
                        self.ui.oilprON.setStyleSheet(
                            'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                            'background-color: #222222; border: 2px outset; border-color: red;')
                    elif self.ui.LIGHTORDARK.currentIndex() == 1:
                        self.ui.oilprON.setStyleSheet(
                            'color: #262626; font-family: Archivo; font-size: 13px; '
                            'background-color: #ffffff; border: 2px outset; border-color: red;')
                else:
                    return

        self.oilprpowerstatus = False
        self.inmaupdatepowerstatus = False
        self.ui.oilprON.clicked.connect(lambda: oilprSTATUSon())

        def volSTATUSon():
            if not self.volonoffstatus:
                if self.volpowerstatus == False:
                    self.volpowerstatus = True

                    def vol():
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.volON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: rgb(255,140,39);')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.volON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: rgb(14,42,199);')
                        self.ui.voltage.updateValue(0)
                        # tkr = self.ui.voltage.value
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr += 0.16666667
                        #     self.ui.voltage.updateValue(tkr)
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr -= 0.16666667
                        #     self.ui.voltage.updateValue(tkr)
                        time.sleep(0.5)
                        self.voltageupdatepowerstatus = True
                        self.volonoffstatus = True
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.volON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: green;')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.volON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: green;')

                    t = threading.Thread(target=vol)
                    t.start()
                    # self.returns.append(extcon.Timers.voltagegaugetimerstart(self))
                    extcon.Timers.voltagegaugetimerstart(self)
                else:
                    return
            else:
                if self.volpowerstatus:
                    self.volpowerstatus = False
                    self.volonoffstatus = False
                    self.voltageupdatepowerstatus = False
                    # self.returns.append(extcon.Timers.voltagegaugetimerstop(self))
                    extcon.Timers.voltagegaugetimerstop(self)
                    if self.ui.LIGHTORDARK.currentIndex() == 0:
                        self.ui.volON.setStyleSheet(
                            'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                            'background-color: #222222; border: 2px outset; border-color: red;')
                    elif self.ui.LIGHTORDARK.currentIndex() == 1:
                        self.ui.volON.setStyleSheet(
                            'color: #262626; font-family: Archivo; font-size: 13px; '
                            'background-color: #ffffff; border: 2px outset; border-color: red;')
                else:
                    return

        self.volpowerstatus = False
        self.voltageupdatepowerstatus = False
        self.ui.volON.clicked.connect(lambda: volSTATUSon())

        def tbfSTATUSon():
            if not self.tbfonoffstatus:
                if self.tbfpowerstatus == False:
                    self.tbfpowerstatus = True

                    def tbf():
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.tbfON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: rgb(255,140,39);')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.tbfON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: rgb(14,42,199);')
                        self.ui.tbf.updateValue(0)
                        # tbf = self.ui.tbf.value
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tbf += 2.5
                        #     self.ui.tbf.updateValue(tbf)
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tbf -= 2.5
                        #     self.ui.tbf.updateValue(tbf)
                        time.sleep(0.5)
                        self.intktempupdatepowerstatus = True
                        self.tbfonoffstatus = True
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.tbfON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: green;')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.tbfON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: green;')

                    t = threading.Thread(target=tbf)
                    t.start()
                    # self.returns.append(extcon.Timers.intaketempgaugetimerstart(self))
                    extcon.Timers.intaketempgaugetimerstart(self)
                else:
                    return
            else:
                if self.tbfpowerstatus:
                    self.tbfpowerstatus = False
                    self.tbfonoffstatus = False
                    self.intktempupdatepowerstatus = False
                    # self.returns.append(extcon.Timers.intaketempgaugetimerstop(self))
                    extcon.Timers.intaketempgaugetimerstop(self)
                    if self.ui.LIGHTORDARK.currentIndex() == 0:
                        self.ui.tbfON.setStyleSheet(
                            'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                            'background-color: #222222; border: 2px outset; border-color: red;')
                    elif self.ui.LIGHTORDARK.currentIndex() == 1:
                        self.ui.tbfON.setStyleSheet(
                            'color: #262626; font-family: Archivo; font-size: 13px; '
                            'background-color: #ffffff; border: 2px outset; border-color: red;')
                else:
                    return

        self.tbfpowerstatus = False
        self.intktempupdatepowerstatus = False
        self.ui.tbfON.clicked.connect(lambda: tbfSTATUSon())

        def fuelprSTATUSon():
            if not self.fuelpronoffstatus:
                if self.fuelprpowerstatus == False:
                    self.fuelprpowerstatus = True

                    def fuelpr():
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.fuelprON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: rgb(255,140,39);')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.fuelprON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: rgb(14,42,199);')
                        self.ui.fuelpressure.updateValue(0)
                        # tkr = self.ui.fuelpressure.value
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr += 10.9166667
                        #     self.ui.fuelpressure.updateValue(tkr)
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr -= 10.9166667
                        #     self.ui.fuelpressure.updateValue(tkr)
                        time.sleep(0.5)
                        self.mafupdatepowerstatus = True
                        self.fuelpronoffstatus = True
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.fuelprON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: green;')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.fuelprON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: green;')

                    t = threading.Thread(target=fuelpr)
                    t.start()
                    # self.returns.append(extcon.Timers.mafgaugetimerstart(self))
                    extcon.Timers.mafgaugetimerstart(self)
                else:
                    return
            else:
                if self.fuelprpowerstatus:
                    self.fuelprpowerstatus = False
                    self.fuelpronoffstatus = False
                    self.mafupdatepowerstatus = False
                    # self.returns.append(extcon.Timers.mafgaugetimerstop(self))
                    extcon.Timers.mafgaugetimerstop(self)
                    if self.ui.LIGHTORDARK.currentIndex() == 0:
                        self.ui.fuelprON.setStyleSheet(
                            'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                            'background-color: #222222; border: 2px outset; border-color: red;')
                    elif self.ui.LIGHTORDARK.currentIndex() == 1:
                        self.ui.fuelprON.setStyleSheet(
                            'color: #262626; font-family: Archivo; font-size: 13px; '
                            'background-color: #ffffff; border: 2px outset; border-color: red;')
                else:
                    return

        self.fuelprpowerstatus = False
        self.mafupdatepowerstatus = False
        self.ui.fuelprON.clicked.connect(lambda: fuelprSTATUSon())

        def fuelSTATUSon():
            if not self.fuelonoffstatus:
                if self.fuelpowerstatus == False:
                    self.fuelpowerstatus = True

                    def fuel():
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.fuelON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: rgb(255,140,39);')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.fuelON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: rgb(14,42,199);')
                        self.ui.fuel.updateValue(0)
                        # tkr = self.ui.fuel.value
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr += -1.66666667
                        #     self.ui.fuel.updateValue(tkr)
                        # for i in range(60):
                        #     time.sleep(0.01)
                        #     tkr -= -1.66666667
                        #     self.ui.fuel.updateValue(tkr)
                        time.sleep(0.5)
                        self.fuelupdatepowerstatus = True
                        self.fuelonoffstatus = True
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.fuelON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: green;')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.fuelON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: green;')

                    t = threading.Thread(target=fuel)
                    t.start()
                    # self.returns.append(extcon.Timers.fuelgaugetimerstart(self))
                    extcon.Timers.fuelgaugetimerstart(self)
                else:
                    return
            else:
                if self.fuelpowerstatus:
                    self.fuelpowerstatus = False
                    self.fuelonoffstatus = False
                    self.fuelupdatepowerstatus = False
                    # self.returns.append(extcon.Timers.fuelgaugetimerstop(self))
                    extcon.Timers.fuelgaugetimerstop(self)
                    if self.ui.LIGHTORDARK.currentIndex() == 0:
                        self.ui.fuelON.setStyleSheet(
                            'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                            'background-color: #222222; border: 2px outset; border-color: red;')
                    elif self.ui.LIGHTORDARK.currentIndex() == 1:
                        self.ui.fuelON.setStyleSheet(
                            'color: #262626; font-family: Archivo; font-size: 13px; '
                            'background-color: #ffffff; border: 2px outset; border-color: red;')
                else:
                    return

        self.fuelpowerstatus = False
        self.fuelupdatepowerstatus = False
        self.ui.fuelON.clicked.connect(lambda: fuelSTATUSon())

        def allSTATUSon():
            if not self.allonoffstatus:
                if self.allpowerstatus == False:
                    self.allpowerstatus = True

                    def all():
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.allON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: rgb(255,140,39);')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.allON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: rgb(14,42,199);')
                        tkr = 0
                        for i in range(60):
                            time.sleep(0.01)
                            tkr += -1.66666667
                        for i in range(60):
                            time.sleep(0.01)
                            tkr -= -1.66666667
                        time.sleep(0.5)
                        self.allupdatepowerstatus = True
                        self.allonoffstatus = True
                        if self.ui.LIGHTORDARK.currentIndex() == 0:
                            self.ui.allON.setStyleSheet(
                                'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                                'background-color: #222222; border: 2px outset; border-color: green;')
                        elif self.ui.LIGHTORDARK.currentIndex() == 1:
                            self.ui.allON.setStyleSheet(
                                'color: #262626; font-family: Archivo; font-size: 13px; '
                                'background-color: #ffffff; border: 2px outset; border-color: green;')

                    t = threading.Thread(target=all)
                    t.start()
                    if not self.revonoffstatus:
                        revonoff()
                    if not self.gearonoffstatus:
                        gearSTATUSon()
                    if not self.speedonoffstatus:
                        speedSTATUSon()
                    if not self.boostonoffstatus:
                        boostSTATUSon()
                    if not self.oilteonoffstatus:
                        oilteSTATUSon()
                    if not self.oilpronoffstatus:
                        oilprSTATUSon()
                    if not self.volonoffstatus:
                        volSTATUSon()
                    if not self.tbfonoffstatus:
                        tbfSTATUSon()
                    if not self.fuelpronoffstatus:
                        fuelprSTATUSon()
                    if not self.fuelonoffstatus:
                        fuelSTATUSon()
                else:
                    return
            else:
                if self.allpowerstatus:
                    self.allpowerstatus = False
                    self.allonoffstatus = False
                    self.allupdatepowerstatus = False
                    if self.revonoffstatus:
                        revonoff()
                    if self.gearonoffstatus:
                        gearSTATUSon()
                    if self.speedonoffstatus:
                        speedSTATUSon()
                    if self.boostonoffstatus:
                        boostSTATUSon()
                    if self.oilteonoffstatus:
                        oilteSTATUSon()
                    if self.oilpronoffstatus:
                        oilprSTATUSon()
                    if self.volonoffstatus:
                        volSTATUSon()
                    if self.tbfonoffstatus:
                        tbfSTATUSon()
                    if self.fuelpronoffstatus:
                        fuelprSTATUSon()
                    if self.fuelonoffstatus:
                        fuelSTATUSon()
                    if self.ui.LIGHTORDARK.currentIndex() == 0:
                        self.ui.allON.setStyleSheet(
                            'color: #cdcdcd; font-family: Archivo; font-size: 13px; '
                            'background-color: #222222; border: 2px outset; border-color: red;')
                    elif self.ui.LIGHTORDARK.currentIndex() == 1:
                        self.ui.allON.setStyleSheet(
                            'color: #262626; font-family: Archivo; font-size: 13px; '
                            'background-color: #ffffff; border: 2px outset; border-color: red;')
                else:
                    return

        self.allpowerstatus = False
        self.allupdatepowerstatus = False
        self.ui.allON.clicked.connect(lambda: allSTATUSon())

        ###############################################

        def ru():
            tk = self.ui.revs.value
            for i in range(10):
                tk += 0.1
                self.ui.revs.updateValue(tk)
                time.sleep(0.01)
            tk += 0.0001
            self.ui.revs.updateValue(tk)

        def rd():
            tk = self.ui.revs.value
            for i in range(10):
                tk -= 0.1
                self.ui.revs.updateValue(tk)
                time.sleep(0.01)
            tk -= 0.0001
            self.ui.revs.updateValue(tk)

        def rut():
            start = threading.Thread(target=ru)
            start.start()

        def rdt():
            start = threading.Thread(target=rd)
            start.start()

        def gup():
            tk = self.ui.gear.value
            tk += 1
            self.ui.gear.updateValue(tk)

        def gdo():
            tk = self.ui.gear.value6
            tk -= 1
            self.ui.gear.updateValue(tk)

        def sigm():
            while True:
                tk = self.ui.gear.value
                for i in range(6):
                    tk += 1
                    self.ui.gear.updateValue(tk)
                    time.sleep(0.5)
                for i in range(6):
                    tk -= 1
                    self.ui.gear.updateValue(tk)
                    time.sleep(0.5)

        def simgear():
            t = threading.Thread(target=sigm)
            t.start()

        ##############################################

        self.ui.SIMS.clicked.connect(lambda: MainWindow.begin(self))

        # self.ui.codeupdater.clicked.connect(lambda: self.returns.append(extcon.Timers.serialPcodes(self)))

        ################################################################################################################

    class editValues():
        def updaterevs(self, value):
            self.ui.revs.updateValue(value)

        def updatebaropres(self, value):
            self.ui.oiltemp.updateValue(value)

        def updateintktemp(self, value):
            self.ui.tbf.updateValue(value)

        def updateclnttemp(self, value):
            self.ui.psi.updateValue(value)

        def updateengload(self, value):
            self.ui.gear.updateValue(value)

        def updatespeed(self, value):
            self.ui.speed.updateValue(value)

        def updateinmfpres(self, value):
            self.ui.oilpressure.updateValue(value)

        def updatemaf(self, value):
            self.ui.maf.updateValue(value)

        def updatevoltage(self, value):
            self.ui.voltage.updateValue(value)

        def updatefuel(self, value):
            self.ui.fuel.updateValue(value)

        def updateMainECODEbox(self, value):
            DUMBFIX = '{ white-space: pre-wrap; }'
            if value == None:
                self.ui.textEdit.setText(
                    f'<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">'
                    f'<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">p, li {DUMBFIX}'
                    f'</style></head><body style=\" font-family:\'Archivo\'; font-size:8pt; font-weight:400; '
                    f'font-style:normal;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; '
                    f'margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" '
                    f'font-size:11.5pt;\">No current P codes.</span></p></body></html>')
            else:
                self.ui.textEdit.setText(
                    f'<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">'
                    f'<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">p, li {DUMBFIX}'
                    f'</style></head><body style=\" font-family:\'Archivo\'; font-size:8pt; font-weight:400; '
                    f'font-style:normal;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; '
                    f'margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" '
                    f'font-size:11.5pt;\">{value}</span></p></body></html>')

    class obdfunctions():
        def pcscheck(self, pcs):
            if pcs == 1:
                return self.baropreupdatepowerstatus
            elif pcs == 2:
                return self.inmaupdatepowerstatus
            elif pcs == 3:
                return self.intktempupdatepowerstatus
            elif pcs == 4:
                return self.mafupdatepowerstatus
            elif pcs == 5:
                return self.clnttempupdatepowerstatus
            elif pcs == 6:
                return self.voltageupdatepowerstatus
            elif pcs == 7:
                return self.engineloadupdatepowerstatus

        def updatenewdata(self, pcs):
            if pcs == 1:
                return self.baropre
            elif pcs == 2:
                return self.inmapres
            elif pcs == 3:
                return self.intaketemp
            elif pcs == 4:
                return self.maf
            elif pcs == 5:
                return self.clnttemp
            elif pcs == 6:
                return self.voltage
            elif pcs == 7:
                return self.engineload

        def updatelastdata(self, pcs):
            if pcs == 1:
                return self.ui.oiltemp.value
            elif pcs == 2:
                return self.ui.oilpressure.value
            elif pcs == 3:
                return self.ui.tbf.value
            elif pcs == 4:
                return self.ui.fuelpressure.value
            elif pcs == 5:
                return self.ui.psi.value
            elif pcs == 6:
                return self.ui.voltage.value
            elif pcs == 7:
                return self.ui.gear.value

        def updatenewnlast(self, pcs):
            if pcs == 1:
                return self.baropre, self.ui.oiltemp.value
            elif pcs == 2:
                return self.inmapres, self.ui.oilpressure.value
            elif pcs == 3:
                return self.intaketemp, self.ui.tbf.value
            elif pcs == 4:
                return self.maf, self.ui.fuelpressure.value
            elif pcs == 5:
                return self.clnttemp, self.ui.psi.value
            elif pcs == 6:
                return self.voltage, self.ui.voltage.value
            elif pcs == 7:
                return self.engineload, self.ui.gear.value
        ################################################################################################################
        #                                           Gauge Updater                                                      #
        ################################################################################################################

        def smooth(self, hmtc, gctd, upti, gtuv, pcs):
            def higher(lastdata, dif, hmtc, gctd, gtuv):
                for i in range(dif):
                    lastdata += hmtc
                    gtuv.updateValue(lastdata)
                    time.sleep(gctd)
            def lower(lastdata, dif, hmtc, gctd, gtuv):
                for i in range(dif):
                    lastdata -= hmtc
                    gtuv.updateValue(lastdata)
                    time.sleep(gctd)

            def check(newdata, lastdata, hmtc, gctd, gtuv):
                if newdata > lastdata:
                    dif = int(newdata) - int(lastdata)
                    higher(lastdata, dif, hmtc, gctd, gtuv)
                elif lastdata > newdata:
                    dif = int(lastdata) - int(newdata)
                    lower(lastdata, dif, hmtc, gctd, gtuv)
                else:
                    gtuv.updateValue(newdata)

            powerchecksystem = MainWindow.obdfunctions.pcscheck(self, pcs)
            while not powerchecksystem:
                powerchecksystem = MainWindow.obdfunctions.pcscheck(self, pcs)
            while powerchecksystem:
                powerchecksystem = MainWindow.obdfunctions.pcscheck(self, pcs)
                newdata, lastdata = MainWindow.obdfunctions.updatenewnlast(self, pcs)
                check(newdata, lastdata, hmtc, gctd, gtuv)
                time.sleep(upti)

        ################################################################################################################
        def serialrpm(self):
            if self.rpmupdatepowerstatus:
                try:
                    res = self.con.query(obd.commands.RPM)
                    rpm = float(str(res.value).replace(' revolutions_per_minute', ''))
                    self.ui.revs.updateValue(rpm)
                except:
                    fillertostopbreak = None
                    # self.returns.append('rpm error')
            else:
                fillertostopbreak = None
                # self.returns.append('rpm offline')

        def serialbaropre(self):
            if self.baropreupdatepowerstatus:
                try:
                    res = self.con.query(obd.commands.BAROMETRIC_PRESSURE)
                    self.baropre = int(float(str(res.value).replace(' kilopascal', '')))
                    #self.ui.oiltemp.updateValue(baropre)
                except:
                    fillertostopbreak = None
                    # self.returns.append('baromertric pressure error')
            else:
                fillertostopbreak = None
                # self.returns.append('barometric pressure offline')

        def serialintaketemp(self):
            if self.intktempupdatepowerstatus:
                try:
                    res = self.con.query(obd.commands.INTAKE_TEMP)
                    self.intaketemp = int(float(str(res.value).replace(' degC', '')))
                    #self.ui.tbf.updateValue(intaketemp)
                    # if intaketemp > self.ui.tbf.value:
                    #     while intaketemp != self.ui.tbf.value:
                    #         update = self.ui.tbf.value + 1
                    #         self.ui.tbf.updateValue(update)
                    #         time.sleep(0.01)
                    # elif intaketemp < self.ui.tbf.value:
                    #     while intaketemp != self.ui.tbf.value:
                    #         update = self.ui.tbf.value - 1
                    #         self.ui.tbf.updateValue(update)
                    #         time.sleep(0.01)
                    # else:
                    #     self.ui.tbf.updateValue(intaketemp)
                except:
                    fillertostopbreak = None
                    # self.returns.append('intake temp error')
            else:
                fillertostopbreak = None
                # self.returns.append('intake temp offline')

        def serialclnttemp(self):
            if self.clnttempupdatepowerstatus:
                try:
                    res = self.con.query(obd.commands.COOLANT_TEMP)
                    self.clnttemp = int(float(str(res.value).replace(' degC', '')))
                    #self.ui.psi.updateValue(clnttemp)
                    # if clnttemp > self.ui.psi.value:
                    #     while clnttemp != self.ui.psi.value:
                    #         update = self.ui.psi.value + 1
                    #         self.ui.psi.updateValue(update)
                    #         time.sleep(0.01)
                    # elif clnttemp < self.ui.psi.value:
                    #     while clnttemp != self.ui.psi.value:
                    #         update = self.ui.psi.value - 1
                    #         self.ui.psi.updateValue(update)
                    #         time.sleep(0.01)
                    # else:
                    #     self.ui.psi.updateValue(clnttemp)
                except:
                    fillertostopbreak = None
                    # self.returns.append('coolant temp error')
            else:
                fillertostopbreak = None
                # self.returns.append('coolant temp offline')

        def serialengineload(self):
            if self.engineloadupdatepowerstatus:
                try:
                    res = self.con.query(obd.commands.ENGINE_LOAD)
                    self.engineload = int(float(str(res.value).replace(' percent', '')))
                    # self.ui.gear.updateValue(self.engineload)
                    # engineload = int(engineload)
                    # lastdata = int(self.ui.gear.value)
                except:
                    fillertostopbreak = None
                    # self.returns.append('engine load error')
            else:
                fillertostopbreak = None
                # self.returns.append('engine load offline')

        def serialspeed(self):
            if self.speedupdatepowerstatus:
                try:
                    res = self.con.query(obd.commands.SPEED)
                    speed = float(str(res.value).replace(' kph', ''))
                    self.ui.speed.updateValue(speed)
                except:
                    fillertostopbreak = None
                    # self.returns.append('speed error')
            else:
                fillertostopbreak = None
                # self.returns.append('speed offline')

        def serialmaf(self):
            if self.mafupdatepowerstatus:
                try:
                    res = self.con.query(obd.commands.MAF)
                    self.maf = int(float(str(res.value).replace(' gps', '')))
                    # print(maf)
                    #self.ui.fuelpressure.updateValue(maf)
                    # if maf > self.ui.fuelpressure.value:
                    #     dif = maf - self.ui.fuelpressure.value
                    #     for i in range(dif):
                    #         update = self.ui.fuelpressure.value + 1
                    #         self.ui.fuelpressure.updateValue(update)
                    #         time.sleep(0.1)
                    # elif maf < self.ui.fuelpressure.value:
                    #     dif = self.ui.fuelpressure.value - maf
                    #     for i in range(dif):
                    #         update = self.ui.fuelpressure.value - 1
                    #         self.ui.fuelpressure.updateValue(update)
                    #         time.sleep(0.1)
                    # else:
                    #     self.ui.fuelpressure.updateValue(maf)
                except:
                    fillertostopbreak = None
                    # self.returns.append('maf error')
            else:
                fillertostopbreak = None
                # self.returns.append('maf offline')

        def serialinmapres(self):
            if self.inmaupdatepowerstatus:
                try:
                    res = self.con.query(obd.commands.INTAKE_PRESSURE)
                    self.inmapres = int(float(str(res.value).replace(' kilopascal', '')))
                    #self.ui.oilpressure.updateValue(inmapres)
                    # if inmapres > self.ui.oilpressure.value:
                    #     while inmapres != self.ui.oilpressure.value:
                    #         update = self.ui.oilpressure.value + 1
                    #         self.ui.oilpressure.updateValue(update)
                    #         time.sleep(0.01)
                    # elif inmapres < self.ui.oilpressure.value:
                    #     while inmapres != self.ui.oilpressure.value:
                    #         update = self.ui.oilpressure.value - 1
                    #         self.ui.oilpressure.updateValue(update)
                    #         time.sleep(0.01)
                    # else:
                    #     self.ui.oilpressure.updateValue(inmapres)
                except:
                    fillertostopbreak = None
                    # self.returns.append('intake manifold pressure error')
            else:
                fillertostopbreak = None
                # self.returns.append('intake manifold pressure offline')

        def serialvoltage(self):
            if self.voltageupdatepowerstatus:
                try:
                    res = self.con.query(obd.commands.ELM_VOLTAGE)
                    voltage = float(str(res.value).replace(' volt', ''))
                    self.voltage = float("{:.1f}".format(voltage))
                    #self.ui.voltage.updateValue(voltage)
                    # if voltage > self.ui.voltage.value:
                    #     while voltage != self.ui.voltage.value:
                    #         update = self.ui.voltage.value + 0.1
                    #         self.ui.voltage.updateValue(update)
                    #         time.sleep(0.01)
                    # elif voltage < self.ui.voltage.value:
                    #     while voltage != self.ui.voltage.value:
                    #         update = self.ui.voltage.value - 0.1
                    #         self.ui.voltage.updateValue(update)
                    #         time.sleep(0.01)
                    # else:
                    #     self.ui.voltage.updateValue(voltage)
                except:
                    fillertostopbreak = None
                    # self.returns.append('voltage error')
            else:
                fillertostopbreak = None
                # self.returns.append('voltage offline');

        def serialPCODE(self):
            try:
                res = (self.con.query(obd.commands.GET_DTC)).value
                # self.returns.append(res)
                # self.returns.append('code read success')
                return res
            except:
                fillertostopbreak = None
                # self.returns.append('code read error')

        ########################################## EXPERIMENTAL DAMPENING ##############################################
        def serialfuel(self):
            def updateneedle(fuel, checkcurrentlevel):
                # dif = checkcurrentlevel - fuel
                # if fuel < checkcurrentlevel:
                #     for i in range(dif):
                #         checkcurrentlevel -= 1
                #         self.ui.fuel.updateValue(checkcurrentlevel)
                #         time.sleep(0.1)
                # elif fuel > checkcurrentlevel:
                #     for i in range(dif):
                #         checkcurrentlevel += 1
                #         self.ui.fuel.updateValue(checkcurrentlevel)
                #         time.sleep(0.1)
                # else:
                #     self.ui.fuel.updateValue(fuel)
                self.ui.fuel.updateValue(fuel)

            if self.fuelupdatepowerstatus:
                try:
                    res = self.con.query(obd.commands.FUEL_LEVEL)
                    fuel = str(int(res.value)).replace(' percent', '')
                    res = self.con.query(obd.commands.SPEED)
                    speed = int(float(str(res.value).replace(' kph', '')))
                    fuel = int(f'-{fuel}')
                    # print(speed)
                    # print(fuel)
                    checkcurrentlevel = self.ui.fuel.value
                    ############# checking if the fuel lever is more or less than the current level ################
                    if speed != 0:
                        if fuel < (checkcurrentlevel - 5):
                            return
                        elif fuel > (checkcurrentlevel + 5):
                            return
                        ####################### if no change then just settings the current value ######################
                        else:
                            updateneedle(fuel, checkcurrentlevel)
                    else:
                        updateneedle(fuel, checkcurrentlevel)
                except:
                    fillertostopbreak = None
                    # self.returns.append('fuel error')
            else:
                fillertostopbreak = None
                # self.returns.append('fuel offline')
        ################################################################################################################

    def makeconnection(self):
        def statupdate(STATUS):
            DUMBFIX = '{white - space: pre-wrap; }'
            self.ui.ConStatus.setText(
                f'<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\"><html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">p, li {DUMBFIX}</style></head><body style=\" font-family:\'Archivo\'; font-size:7.9pt; font-weight:400; font-style:normal;\"><p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:15pt;\">CURRENT CONNECTION STATUS: {STATUS}</span></p></body></html>')

        def serialconnect():
            try:
                time.sleep(1)
                self.con = obd.OBD('COM3')
                # self.returns.append(self.con)
                statupdate(self.con.status())
                self.serialconnecttimer.stop()
            except:
                return

        self.serialconnecttimer = QtCore.QTimer()
        self.serialconnecttimer.timeout.connect(serialconnect)
        self.serialconnecttimer.start()

    def begin(self):
        t = threading.Thread(target=lambda: MainWindow.revs(self))
        t.start()

    def revs(self):
        self.ui.revs.updateValue(0)
        self.ui.speed.updateValue(0)
        self.ui.psi.updateValue(50)
        self.ui.oiltemp.updateValue(0)
        self.ui.oilpressure.updateValue(0)
        self.ui.voltage.updateValue(8)
        self.ui.tbf.updateValue(0)
        self.ui.fuelpressure.updateValue(0)
        self.ui.fuel.updateValue(0)
        self.ui.gear.updateValue(0)
        tkr = self.ui.revs.value
        tks = self.ui.speed.value
        tkp = self.ui.psi.value
        tkot = self.ui.oiltemp.value
        tkop = self.ui.oilpressure.value
        tkv = self.ui.voltage.value
        tbf = self.ui.tbf.value
        tkfp = self.ui.fuelpressure.value
        tkf = self.ui.fuel.value
        tkg = self.ui.gear.value
        for i in range(60):
            time.sleep(0.01)
            tkr += 133.333333
            tks += 4
            tkp += 1.66666667
            tkot += 2.5
            tkop += 1.66666667
            tkv += 0.16666667
            tbf += 2.5
            tkfp += 10.9166667
            tkf += -1.66666667
            tkg += 1.66666667
            self.ui.revs.updateValue(tkr)
            self.ui.speed.updateValue(tks)
            self.ui.psi.updateValue(tkp)
            self.ui.oiltemp.updateValue(tkot)
            self.ui.oilpressure.updateValue(tkop)
            self.ui.voltage.updateValue(tkv)
            self.ui.tbf.updateValue(tbf)
            self.ui.fuelpressure.updateValue(tkfp)
            self.ui.fuel.updateValue(tkf)
            self.ui.gear.updateValue(tkg)
        for i in range(60):
            time.sleep(0.01)
            tkr -= 133.333333
            tks -= 4
            tkp -= 1.66666667
            tkot -= 2.5
            tkop -= 1.66666667
            tkv -= 0.16666667
            tbf -= 2.5
            tkfp -= 10.9166667
            tkf -= -1.66666667
            tkg -= 1.66666667
            self.ui.revs.updateValue(tkr)
            self.ui.speed.updateValue(tks)
            self.ui.psi.updateValue(tkp)
            self.ui.oiltemp.updateValue(tkot)
            self.ui.oilpressure.updateValue(tkop)
            self.ui.voltage.updateValue(tkv)
            self.ui.tbf.updateValue(tbf)
            self.ui.fuelpressure.updateValue(tkfp)
            self.ui.fuel.updateValue(tkf)
            self.ui.gear.updateValue(tkg)


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())

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
