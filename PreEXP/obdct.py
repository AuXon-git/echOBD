import obd
import serial
import time
import io
import os
import sys
import string
import math
from obd import OBDCommand, Unit
from obd.protocols import ECU
from obd.utils import bytes_to_int

while True:
    #selection = int(input("Please select which test to perform: "))
    selection = 4

    # c = obd.OBD('COM1')
    # cmd = obd.commands.RPM
    # while True:
    #     response = c.query(cmd)
    #     print(response.value)
    #     time.sleep(0.1)

    if selection == 1:
        c = obd.OBD('COM1')
        def rpm(messages):
            d = messages[0].data
            d = d[2:]
            v = bytes_to_int(d) / 4.0
            return v * Unit.RPM
        co = OBDCommand("RPM", "Engine RPM", b"010C", 2, rpm, ECU.ENGINE, True)
        response = c.query(co, force=True)
        print(response.value)
        def fueltl(messages):
            d = messages[0].data
            d = d[2:]
            v = bytes_to_int(d) / 4.0
            return v * Unit.percentage
        co = OBDCommand("Fuel Level", "Fuel Tank Level", b"012F", 1, fueltl, ECU.ENGINE, True)
        response = c.query(co, force=True)
        print(response.value)

    if selection == 2:
        ser = serial.Serial('COM1', 38400, timeout=1)
        ser.write(b"01 0D \r")
        speed_hex = str(ser.readline()).split(' ')
        #speed = float(int('0x' + speed_hex[3], 0))
        speed = eval('0x' + speed_hex[3], 0)
        print(speed)

    if selection == 3:
        ser = serial.Serial("COM1")
        ser.baudrate = 38400
        s = input('Enter command --> ')
        print ('command = ' + s)
        ser.write(bytes(s + '\r\n', encoding = 'utf-8'))
        ser.timeout = 1
        response = ser.read(999).decode('utf-8')
        print(response)
        ser.close()

    # ser = serial.Serial("COM1")
    # ser.baudrate = 38400
    # s = input('Enter AT command --> ')
    # print ('AT command = ' + s)
    # ser.write(bytes(s + '\r\n', encoding = 'utf-8'))
    # ser.timeout = 1
    # response = ser.read(999).decode('utf-8')
    # print(response)
    # ser.close()

    # ser = serial.Serial("COM1")
    # ser.baudrate = 38400
    # s = input('Enter command --> ')
    # print ('command = ' + s)
    # ser.write(bytes(s + '\r\n', encoding = 'utf-8'))
    # ser.timeout = 1
    # response = ser.read(999).decode('utf-8')
    # print(response)
    # ser.close()

    # ser = serial.Serial('COM1', 38400, timeout=1)
    # while True:
    #     ser.write(b'\x0C12')
    #     rpm_hex = ser.readline().split('  ')
    #     rpm = float(int('0x' + rpm_hex[3], 0))
    #     print(rpm)
    #     time.sleep(0.1)

    if selection == 4:
        port = serial.Serial("COM1", baudrate=38400, timeout=0.025, bytesize=8, stopbits=1)

        def flush():
            port.flushInput()
            port.flushOutput()

        flush()
        flush()

        #port.write(b"ATDP\r")
        #rcv = port.readline()
        #print("Supported OBD II Protocol is " + repr(rcv))

        # def one(rcv):  # Calculating the decimal value of 1 byte hexadecimal numbers
        #     r = rcv.split(b'\r', 1)
        #     print(r)
        #     v = r[1]
        #     print("\n" + str(v))
        #     v = v[6:-3]  # A substring from index 6 to -3 including both - Python indexing start from 0
        #     vspeed = int(v, 16)
        #     return vspeed
        #
        # def two(rcv):  # Calculating the decimal value of 2 bytes hexadecimal numbers
        #     r = rcv.split(b'\r', 1)
        #     v = r[1]
        #     # bol = pid_supported(v)
        #     # if bol != 'false'
        #     v = v[6:-3]
        #     a = int(v[0:2], 16)
        #     b = int(v[3:5], 16)
        #     return {'A': a, 'B': b}

        def one(rcv): # 1 byte return calculator
            r = rcv.split(b'\r', 1)
            v = r[1]
            v = v[6:-3]
            a = int(v, 16)
            return a

        def two(rcv): # 2 byte return calculator
            r = rcv.split(b'\r', 1)
            v = r[1]
            v = v[6:-3]
            a = int(v[0:2], 16)
            b = int(v[3:5], 16)
            return {'A': a, 'B': b}

        def four(rcv): # 4 byte return calculator
            print(rcv)
            r = rcv.split(b'\r', 1)
            v = r[1]
            v = v[6:-3]
            a = int(v[0:2], 16)
            b = int(v[3:5], 16)
            c = int(v[6:8], 16)
            d = int(v[9:11], 16)
            return {'A': a, 'B': b, 'C': c, 'D': d}

        def five(rcv): # 5 byte return calculator HIGHLY EXPERIMENTAL
            r = rcv.split(b'\r', 1)
            v = r[1]
            v = v[6:-3]
            a = int(v[0:2], 16)
            b = int(v[3:5], 16)
            c = int(v[6:8], 16)
            d = int(v[9:11], 16)
            e = int(v[12:14], 16)
            return {'A': a, 'B': b, 'C': c, 'D': d, 'E': e}

        def speed(): # 1 byte return example
            flush()
            port.write(b"010D\r")
            rcv = port.readline()
            speed = one(rcv)
            print("\nVehicle Speed: " + repr(speed) + "Km/H.")
            return speed

        def fuelpressure(): # 1 byte return example
            flush()
            port.write(b"010D\r")
            rcv = port.readline()
            print(rcv)
            fp = one(rcv)
            fp = fp*(100/255)
            print("\nFuel Pressure: " + repr(fp) + "kPa.")
            return fp

        def rpm(): # 2 byte return example
            flush()
            port.write(b"010C\r")
            rcv = port.readline()
            r = two(rcv)
            a = r['A']; b = r['B']
            rpm = (a * 256 + b) / 4
            print("\nEngine RPM:" + repr(rpm) + "rpm.")
            return rpm

        def gear(): # 4 byte return example
            flush()
            port.write(b"01A4\r")
            rcv = port.readline()
            r = four(rcv)
            a = r['A']; b = r['B']; c = r['C']; d = r['D']
            gear = (c * 256 + d) / 1000
            print("\nCurrent GEAR:" + repr(gear))
            return gear

        def odometer(): # 4 byte return example
            flush()
            port.write(b"015C\r")
            rcv = port.readline()
            print(rcv)
            r = one(rcv)
            #a = r['A']; b = r['B']
            odometer = r -40
            print("\nOil Temp: " + repr(odometer) + "C")
            return odometer

        # def speed():
        #     flush()
        #     port.write(b"010D\r")
        #     rcv = port.readline()
        #     print(rcv)
        #     # print("\n"+repr(r))
        #     vspeed = one(rcv)
        #     print("\nVehicle Speed: " + repr(rcv) + "Km/H.")
        #     return vspeed
        #
        # def rpm():
        #     flush()
        #     port.write(b"010C\r")
        #     rcv = port.readline()
        #     print("\n" + repr(rcv))
        #     r = two(rcv)
        #     a = r['A'];
        #     b = r['B']
        #     rpm = (a * 256 + b) / 4
        #     print("\nEngine RPM:" + repr(rpm) + "rpm.")
        #     return rpm
        #     # print a
        #     # print b

        # def gear():
        #     flush()
        #     port.write(b"01A4\r")
        #     rcv = port.readline()
        #     print("\n" + repr(rcv))
        #     return rcv

        def cooltemp():
            flush()
            port.write(b"015C\r")
            rcv = port.readline()
            tmp = one(rcv)
            t = tmp - 40
            print("\nEngine Coolant Temp.:" + repr(t) + " degree Celsius.")

        def intaketemp():
            flush()
            port.write(b"010F\r")
            rcv = port.readline()
            tmp = one(rcv)
            tmp = tmp - 40
            print("\nIntake Air Temp: " + repr(tmp) + " degree Celsius.")

        def throttle():
            flush()
            port.write(b"0111\r")
            rcv = port.readline()
            thr = one(rcv)
            thr = thr * 100 / 255
            print("\nThrottle position:" + repr(thr) + " %.")

        def fuellevel():
            flush()
            port.write(b"012F\r")
            rcv = port.readline()
            thr = one(rcv)
            thr = thr * 100 / 255
            print("\nFuel Level:" + repr(thr) + " %.")

        def runtime():
            flush()
            port.write(b"010F\r")
            rcv = port.readline()
            rt = two(rcv)
            a = rt['A'];
            b = rt['B']
            time = a * 256 + b
            print("\nRun Time since Engine start: " + repr(time) + " seconds")

        def engineload():
            flush()
            port.write(b"0104\r")
            rcv = port.readline()
            lv = one(rcv)
            elv = lv * 100 / 255
            print("\nCalculated Engine Load Value: " + repr(elv) + " %")

        def distance():  # Distance travelled since codes cleared
            flush()
            port.write(b"0131\r")
            rcv = port.readline()
            dis = two(rcv)
            a = dis['A'];
            b = dis['B']
            dt = a * 256 + b
            print("\nDistance travelled since codes cleared: " + repr(dt) + " Km")

        def ambient():
            flush()
            port.write(b"0146\r")
            rcv = port.readline()
            a = one(rcv)
            a = a - 40
            print("\nAmbient Air Temp: " + repr(a) + " degree Celsius")

        # Does not humidity and other parameters of the environment
        def fuelrate():
            flush()
            port.write(b"015E\r")
            rcv = port.readline()
            v = two(rcv)
            a = v['A'];
            b = v['B']
            rate = (a * 256 + b) * (0.05)
            print("\nEngine Fuel Rate: " + repr(rate) + " L/h")

        def battery():
            flush()
            port.write(b"015B\r")
            rcv = port.readline()
            v = one(rcv)
            time = v * 100 / 255
            print("\nHybrid battery remaining life: " + repr(time) + " %")

        def fueleconomy():  # maf sensor supported
            flush()
            vspeed = speed()
            flush()
            port.write(b"0110\r")
            rcv = port.readline()
            f = two(rcv)
            a = f['A']; b = f['B']
            maf = (a * 256 + b) / 100
            mpg = (7.107 * vspeed) / maf
            print("\nInstantaneous fuel economy is: " + repr(mpg) + " MPG")

        def fuel_economy():
            flush()
            port.write(b"010B\r")
            rcv = port.readline()
            imap = one(rcv)
            maf = (imap / 120) * (0.85) * 4 * (28.97) / (8.314)
            print(maf)
            vspeed = speed()
            mpg = (7.107 * vspeed) / maf
            print("\nInstantaneous fuel economy is:" + repr(mpg) + " MPG")

        def shortterm():
            flush()
            port.write(b"0106\r")
            rcv = port.readline()
            st = one(rcv)
            st = ((st - 128) / 128) * 100
            print("\nShort term fuel bank: " + repr(st) + " %")

        def longterm():
            flush()
            port.write(b"0108\r")
            rcv = port.readline()
            lt = one(rcv)
            lt = ((lt - 128) / 128) * 100
            print("\nLong term fuel bank: " + repr(lt) + " %")

        def fuel_consum():
            flush()
            rp = rpm()
            th = throttle()

        def geartesting(): # 4 byte return example
            flush()
            #port.write(b"01A4\r")
            #port.write(b"atdp\r")
            port.write(b"01A4\r")
            rcv = port.readline()
            print(rcv)
            return gear

        def voltage():
            flush()
            port.write(bytes('atrv\r\n', encoding='utf-8'))
            rcv = port.read(999).decode('utf-8')
            rcvv = []
            for i in rcv:
                rcvv.append(i)
            rcvvv = str(rcvv[5]+rcvv[6]+rcvv[7]+rcvv[8])[0:]
            print(float(rcvvv))
            return rcvvv

        #print(one(b'7E8037F2213'))

        while True:
            # voltage()
            # speed()
            rpm()
            #print(return1)
            #fuelpressure()
            #geartesting()
            #odometer()
            #fuellevel()
            # cooltemp()
            # intaketemp()
            # throttle()
            # engineload()
            # ambient()
            # runtime()
            # distance()
            # fuelrate()
            # battery()
            # fueleconomy()
            # fuel_economy()
            # shortterm()
            # longterm()
            print("\n\n")
            #time.sleep(0.5)