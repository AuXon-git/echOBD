import serial
# import logging
import re
import obd


def serialconnect():
    ser = serial.Serial("COM1", baudrate=38400, timeout=0.025, bytesize=8, stopbits=1)
    def flush():
        ser.flushInput()
        ser.flushOutput()
    flush()

    buffer = bytearray()
    # logger = logging.getLogger(__name__)

    ser.write(b"010C\r")
    returna = ser.readline()
    flush()

    ser.write(b"010C\r")
    returnb = ser.read(ser.in_waiting or 1)
    buffer.extend(returnb)
    # logger.debug("read: " + repr(buffer)[10:-1])
    buffer = re.sub(b"\x00", b"", buffer)
    string = buffer.decode("utf-8", "ignore")
    lines = [s.strip() for s in re.split("[\r\n]", string) if bool(s)]
    flush()

    print(f'type a: {returna}\ntype b: {returnb}\nlines: {lines}')

#serialconnect()

con = obd.OBD('COM1')
cmd = obd.commands.RPM
while True:
    res = con.query(cmd)
    print(res.value)











def hex_to_int(str):
    i = eval("0x" + str, {}, {})
    return i


def dtc_decrypt(code):
    # first byte is byte after PID and without spaces
    num = hex_to_int(code[:2])  # A byte
    res = []

    if num & 0x80:  # is mil light on
        mil = 1
    else:
        mil = 0

    # bit 0-6 are the number of dtc's.
    num = num & 0x7f

    res.append(num)
    res.append(mil)

    numB = hex_to_int(code[2:4])  # B byte

    for i in range(0, 3):
        res.append(((numB >> i) & 0x01) + ((numB >> (3 + i)) & 0x02))

    numC = hex_to_int(code[4:6])  # C byte
    numD = hex_to_int(code[6:8])  # D byte

    for i in range(0, 7):
        res.append(((numC >> i) & 0x01) + (((numD >> i) & 0x01) << 1))

    res.append(((numD >> 7) & 0x01))  # EGR SystemC7  bit of different

    return res


def hex_to_bitstring(str):
    bitstring = ""
    for i in str:
        # silly type safety, we don't want to eval random stuff
        if type(i) == type(''):
            v = eval("0x%s" % i)
            if v & 8:
                bitstring += '1'
            else:
                bitstring += '0'
            if v & 4:
                bitstring += '1'
            else:
                bitstring += '0'
            if v & 2:
                bitstring += '1'
            else:
                bitstring += '0'
            if v & 1:
                bitstring += '1'
            else:
                bitstring += '0'
    return bitstring