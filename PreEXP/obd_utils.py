import serial

def scanSerial():
    available = []
    for i in range(10):
        try:
            s = serial.Serial('/dev/rfcomm'+str(i))
            available.append((str(s.port)))
            s.close()
        except serial.SerialException:
            pass
    return available