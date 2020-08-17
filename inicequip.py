"""
Mudança realizada em 10/07:
Coloquei a numeração da bomba somente quando o serial não estiver aberto,
para que se chamar a função outra vez, ela não refaça isso.
"""
from configserial import *
import time

def masterflex775030(porta):
    ser1 = configserial(porta, 4800, 7, "Odd", 1)
    if ser1.is_open == False:
        ser1.open()
        ser1.write("\x05".encode("ascii"))
        time.sleep(1)
        ser1.write("\x02P01\x0d".encode("ascii"))
    return ser1

def galaxy170r(porta):
    ser2 = configserial(porta, 19200, 8, "None", 1)
    if ser2.is_open == False:
        ser2.open()
    return ser2
        
def MS7H550S(porta):
    ser3 = configserial(porta, 9600, 8, "None", 1)
    if ser3.is_open == False:
        ser3.open()
    return ser3
