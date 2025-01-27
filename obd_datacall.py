from PyQt5 import QtCore

from main import MainWindow as obd
from PyQt5.QtCore import Qt, QTimer
import threading


class Timers:
    def __init__(self):
        self.rpminterval = 2
        self.engineloadinterval = 501
        self.speedinterval = 3
        self.clnttempinterval = 1001
        self.baropreinterval = 1002
        self.inmapresinterval = 1003
        self.voltinterval = 1004
        self.intaketempinterval = 1005
        self.mafinterval = 1006
        self.fuelinterval = 15000
    ####################################################################################################################
    #                                                  RPM CONTROLLER                                                  #
    ####################################################################################################################
    def rpmgaugetimerstart(self):
        def x():
            obd.obdfunctions.serialrpm(self)

        try:
            self.rpmgaugetimerupdate = QtCore.QTimer()
            self.rpmgaugetimerupdate.timeout.connect(x)
            self.rpmgaugetimerupdate.setInterval(self.rpminterval)
            self.rpmgaugetimerupdate.start()
            return 'begun timer rpm'
        except:
            return 'timer start failure rpm'

    def rpmgaugetimerstop(self):
        try:
            self.rpmgaugetimerupdate.stop()
            return 'timer stopped rpm'
        except:
            return 'timer stop failure rpm'

    ####################################################################################################################
    #                                          ENGINE LOAD CONTROLLER                                                  #
    ####################################################################################################################
    def engineloadgaugetimerstart(self):
        def x():
            obd.obdfunctions.serialengineload(self)

        try:
            self.engineload = 0
            self.englgaugetimerupdate = QtCore.QTimer()
            self.englgaugetimerupdate.timeout.connect(x)
            self.englgaugetimerupdate.setInterval(self.engineloadinterval)
            self.englgaugetimerupdate.start()
            t = threading.Thread(
                target=lambda: obd.obdfunctions.smooth(self, 1, 0.01, 0.5, self.ui.gear, 7))
            t.start()

            return 'begun timer engine load'
        except:
            return 'timer start failure engine load'

    def engineloadgaugetimerstop(self):
        try:
            self.englgaugetimerupdate.stop()
            return 'timer stopped engine load'
        except:
            return 'timer stop failure engine load'

    ####################################################################################################################
    #                                                SPEED CONTROLLER                                                  #
    ####################################################################################################################
    def speedgaugetimerstart(self):
        def x():
            obd.obdfunctions.serialspeed(self)

        try:
            self.speedgaugetimerupdate = QtCore.QTimer()
            self.speedgaugetimerupdate.timeout.connect(x)
            self.speedgaugetimerupdate.setInterval(self.speedinterval)
            self.speedgaugetimerupdate.start()
            return 'begun timer speed'
        except:
            return 'timer start failure speed'

    def speedgaugetimerstop(self):
        try:
            self.speedgaugetimerupdate.stop()
            return 'timer stopped speed'
        except:
            return 'timer stop failure speed'

    ####################################################################################################################
    #                                         COOLANT TEMP CONTROLLER                                                  #
    ####################################################################################################################
    def clnttempgaugetimerstart(self):
        def x():
            obd.obdfunctions.serialclnttemp(self)

        try:
            self.clntgaugetimerupdate = QtCore.QTimer()
            self.clntgaugetimerupdate.timeout.connect(x)
            self.clntgaugetimerupdate.setInterval(self.clnttempinterval)
            self.clntgaugetimerupdate.start()
            t = threading.Thread(
                target=lambda: obd.obdfunctions.smooth(self, 1, 0.01, 1,
                                                       self.ui.psi, 5))
            t.start()
            return 'begun timer coolant temp'
        except:
            return 'timer start failure coolant temp'

    def clnttempgaugetimerstop(self):
        try:
            self.clntgaugetimerupdate.stop()
            return 'timer stopped coolant temp'
        except:
            return 'timer stop failure coolant temp'

    ####################################################################################################################
    #                                   BAROMETER PRESSURE CONTROLLER                                                  #
    ####################################################################################################################
    def baropregaugetimerstart(self):
        def x():
            obd.obdfunctions.serialbaropre(self)

        try:
            self.baropregaugetimerupdate = QtCore.QTimer()
            self.baropregaugetimerupdate.timeout.connect(x)
            self.baropregaugetimerupdate.setInterval(self.baropreinterval)
            self.baropregaugetimerupdate.start()
            t = threading.Thread(
                target=lambda: obd.obdfunctions.smooth(self, 1, 0.01, 1,
                                                       self.ui.oiltemp, 1))
            t.start()
            return 'begun timer barometer pressure'
        except:
            return 'timer start failure barometer pressure'

    def baropregaugetimerstop(self):
        try:
            self.baropregaugetimerupdate.stop()
            return 'timer stopped barometer pressure'
        except:
            return 'timer stop failure barometer pressure'

    ####################################################################################################################
    #                                   INTAKE MANIFOLD PRESSURE CONTROLLER                                            #
    ####################################################################################################################
    def inmapresgaugetimerstart(self):
        def x():
            obd.obdfunctions.serialinmapres(self)

        try:
            self.inmapresgaugetimerupdate = QtCore.QTimer()
            self.inmapresgaugetimerupdate.timeout.connect(x)
            self.inmapresgaugetimerupdate.setInterval(self.inmapresinterval)
            self.inmapresgaugetimerupdate.start()
            t = threading.Thread(
                target=lambda: obd.obdfunctions.smooth(self, 1, 0.01, 1,
                                                       self.ui.oilpressure, 2))
            t.start()
            return 'begun timer intake manifold pressure'
        except:
            return 'timer start failure intake manifold pressure'

    def inmapresgaugetimerstop(self):
        try:
            self.inmapresgaugetimerupdate.stop()
            return 'timer stopped intake manifold pressure'
        except:
            return 'timer stop failure intake manifold pressure'

    ####################################################################################################################
    #                                                    VOLTAGE CONTROLLER                                            #
    ####################################################################################################################
    def voltagegaugetimerstart(self):
        def x():
            obd.obdfunctions.serialvoltage(self)

        try:
            self.voltagegaugetimerupdate = QtCore.QTimer()
            self.voltagegaugetimerupdate.timeout.connect(x)
            self.voltagegaugetimerupdate.setInterval(self.voltinterval)
            self.voltagegaugetimerupdate.start()
            t = threading.Thread(
                target=lambda: obd.obdfunctions.smooth(self, 0.1, 0.01, 1,
                                                       self.ui.voltage, 6))
            t.start()
            return 'begun timer voltage'
        except:
            return 'timer start failure voltage'

    def voltagegaugetimerstop(self):
        try:
            self.voltagegaugetimerupdate.stop()
            return 'timer stopped voltage'
        except:
            return 'timer stop failure voltage'

    ####################################################################################################################
    #                                                INTAKE TEMP CONTROLLER                                            #
    ####################################################################################################################
    def intaketempgaugetimerstart(self):
        def x():
            obd.obdfunctions.serialintaketemp(self)

        try:
            self.intaketgaugetimerupdate = QtCore.QTimer()
            self.intaketgaugetimerupdate.timeout.connect(x)
            self.intaketgaugetimerupdate.setInterval(self.intaketempinterval)
            self.intaketgaugetimerupdate.start()
            t = threading.Thread(
                target=lambda: obd.obdfunctions.smooth(self, 1, 0.01, 1,
                                                       self.ui.tbf, 3))
            t.start()
            return 'begun timer intake temp'
        except:
            return 'timer start failure intake temp'

    def intaketempgaugetimerstop(self):
        try:
            self.intaketgaugetimerupdate.stop()
            return 'timer stopped intake temp'
        except:
            return 'timer stop failure intake temp'

    ####################################################################################################################
    #                                                   MAF CONTROLLER                                                 #
    ####################################################################################################################
    def mafgaugetimerstart(self):
        def x():
            obd.obdfunctions.serialmaf(self)

        try:
            self.mafgaugetimerupdate = QtCore.QTimer()
            self.mafgaugetimerupdate.timeout.connect(x)
            self.mafgaugetimerupdate.setInterval(self.mafinterval)
            self.mafgaugetimerupdate.start()
            t = threading.Thread(
                target=lambda: obd.obdfunctions.smooth(self, 1, 0.01, 1,
                                                       self.ui.fuelpressure, 4))
            t.start()
            return 'begun timer maf'
        except:
            return 'timer start failure maf'

    def mafgaugetimerstop(self):
        try:
            self.mafgaugetimerupdate.stop()
            return 'timer stopped maf'
        except:
            return 'timer stop failure maf'

    ####################################################################################################################
    #                                                  FUEL CONTROLLER                                                 #
    ####################################################################################################################
    def fuelgaugetimerstart(self):
        def x():
            obd.obdfunctions.serialfuel(self)

        try:
            self.fuelgaugetimerupdate = QtCore.QTimer()
            self.fuelgaugetimerupdate.timeout.connect(x)
            self.fuelgaugetimerupdate.setInterval(self.fuelinterval)
            self.fuelgaugetimerupdate.start()
            return 'begun timer fuel'
        except:
            return 'timer start failure fuel'

    def fuelgaugetimerstop(self):
        try:
            self.fuelgaugetimerupdate.stop()
            return 'timer stopped fuel'
        except:
            return 'timer stop failure fuel'

    ####################################################################################################################

    ####################################################################################################################
    #                                                P CODE CONTROLLER                                                 #
    ####################################################################################################################
    def serialPcodes(self):
        def x():
            obd.obdfunctions.serialPCODE(self)
        try:
            obd.editValues.updateMainECODEbox(self, x())
        except:
            return 'code read error'
    ####################################################################################################################
