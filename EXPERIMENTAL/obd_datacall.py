from PyQt5 import QtCore

from EXPmain import MainWindow as obd
from PyQt5.QtCore import Qt, QTimer


class Timers:
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
            self.rpmgaugetimerupdate.start(0)
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
            self.englgaugetimerupdate = QtCore.QTimer()
            self.englgaugetimerupdate.timeout.connect(x)
            self.englgaugetimerupdate.setInterval(self.engineloadinterval)
            self.englgaugetimerupdate.start()
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
            self.speedgaugetimerupdate.setInterval(2)
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
            self.clntgaugetimerupdate.setInterval(20)
            self.clntgaugetimerupdate.start()
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
            self.baropregaugetimerupdate.setInterval(22)
            self.baropregaugetimerupdate.start()
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
            self.inmapresgaugetimerupdate.setInterval(24)
            self.inmapresgaugetimerupdate.start()
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
            self.voltagegaugetimerupdate.setInterval(50)
            self.voltagegaugetimerupdate.start()
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
            self.intaketgaugetimerupdate.setInterval(28)
            self.intaketgaugetimerupdate.start()
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
            self.mafgaugetimerupdate.setInterval(28)
            self.mafgaugetimerupdate.start()
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
            self.fuelgaugetimerupdate.setInterval(15000)
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
            return 'code read success'
        except:
            return 'code read error'
    ####################################################################################################################
