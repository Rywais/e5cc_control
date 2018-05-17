#!/usr/bin/python3

import serial,time

ser = serial.Serial('/dev/ttyUSB0',9600)
ser.parity = serial.PARITY_EVEN
data = bytes.fromhex('010800001234ED7C')
ser.write(data)
time.sleep(0.2)
print("Sent:", data)
print("Resp:", ser.read(8))
ser.close()
