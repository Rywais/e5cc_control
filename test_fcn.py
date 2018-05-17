#!/usr/bin/python3

from e5cc import crc16

msg = bytearray()
msg.append(1)
print('Function codes:')
print('03 - Read Variable (multiple)')
print('16 - Write Variable (multiple)')
print('06 - Write Variable (Single/Operation Command)')
print('08 - Echoback Test')
fc = input("Please enter your Function Code: ")
fc = int(fc, 16)
msg.append(fc)
data = input('Please enter your data (Hex Format):')
for i in range(int(len(data)/2)):
  hex_str = ''.join([ data[2*i], data[2*i+1] ])
  msg.append(int(hex_str,16))

crc = crc16(msg)
msg.append(crc[0])
msg.append(crc[1])

print(msg)

#TESTING CODE FOLLOWS

import serial,time
ser = serial.Serial('/dev/ttyUSB0',9600)
ser.parity = serial.PARITY_EVEN
ser.write(msg)
time.sleep(0.20)
print("Sent:", msg)
resp_len = ser.in_waiting
resp = ser.read(resp_len)
print(resp.hex())
ser.close()
