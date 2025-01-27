# import threading
# from PyQt5 import QtCore
# import time
#
# from main import MainWindow
#
# class trackTimerControllers:
#     def startup(self):
#         finalreturn = 'CURRENT TIME: 00:00:00'
#         MainWindow.TimerFunctions.updatetracktimeinrealtime(self, finalreturn)
#         self.tominresetvalue = 0
#         self.elapsedminutes = 0
#         self.stopwatchgo = False
#         MainWindow.TimerFunctions.updatetracktimeinrealtime(self)
#
#     def tracktimer(self):
#         def start():
#             MainWindow.editValues.updatetracktimestarttext(self, 'STOP TIMER')
#             self.begin = time.time()
#             while self.stopwatchgo:
#                 self.end = time.time()
#                 self.elapsedseconds = self.end - self.begin
#                 self.elapsedmilliseconds = (round(self.elapsedseconds * 100) - (int(self.elapsedseconds) * 100))
#                 if int(self.elapsedmilliseconds) <= 9:
#                     self.elapsedmilliseconds = f'0{self.elapsedmilliseconds}'
#                 if int(self.elapsedmilliseconds) == 100:
#                     self.elapsedmilliseconds = '00'
#                 if (int(self.elapsedseconds) - self.tominresetvalue) <= 9:
#                     self.elapsedseconds = f'0{int(self.elapsedseconds) - self.tominresetvalue}'
#                 if (int(self.elapsedseconds) - self.tominresetvalue) >= 10:
#                     self.elapsedseconds = int(self.elapsedseconds - self.tominresetvalue)
#                 if (int(self.elapsedseconds) - self.tominresetvalue) == 60:
#                     self.tominresetvalue += 60
#                     self.elapsedminutes += 1
#                 if self.elapsedminutes <= 9:
#                     self.fminr = f'0{self.elapsedminutes}'
#                 if self.elapsedminutes >= 10:
#                     self.fminr = self.elapsedminutes
#                 self.finalreturn = str(f'CURRENT TIME: {self.fminr}:{self.elapsedseconds}:{self.elapsedmilliseconds}')
#                 time.sleep(0.01)
#         if self.stopwatchgo:
#             MainWindow.editValues.updatetracktimestarttext(self, 'START TIMER')
#             MainWindow.plotControllers.stopobdplot(self)
#             self._update_timer.stop()
#             self.stopwatchgo = False
#         else:
#             self.stopwatchgo = True
#             MainWindow.plotControllers.startobdplotting(self)
#             self._update_timer = QtCore.QTimer()
#             self._update_timer.timeout.connect(MainWindow.TimerFunctions.updatetracktimeinrealtime(self))
#             self._update_timer.start(10)
#             t = threading.Thread(target=lambda:start())
#             t.start()