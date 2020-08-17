import serial

def configserial(port, baudrate, bytesize, parity, stopbits):
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = baudrate
    ser.bytesize = bytesize
    ser.parity = parity[0]
    ser.stopbits = stopbits
    return ser
