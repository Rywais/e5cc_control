#!/usr/bin/python3

import time, serial

# All addresses will be denoted in Two-Byte Mode Format until further notice...
CMD_READ_VAR_MULTIPLE = '03'
CMD_WRITE_FILE_MULTIPLE = '10'
CMD_WRITE_VAR_SINGLE = '06'
CMD_ECHO = '08'

ADDR_PV = '2000' #Address for reading current temperature
ADDR_SV = '2601' #Address for setting desired temperature
ADDR_SV_UPPER_LIM = '2d0f'
ADDR_SV_LOWER_LIM = '2d10'
ADDR_PID_ONOFF = '2d14' #Address for setting PID or ON/OFF control schemes
ADDR_COMMAND = '0000'

PT100_SCALE_FACTOR = 0.1 #Degrees Celcius per Engineering Unit

VAL_PID = '0001'
VAL_ONOFF = '0000'
VAL_START = '0100'
VAL_STOP = '0101'
VAL_SETUP_1 = '0700'
VAL_SOFT_RESET = '0600'
VAL_AUTO_0 = '0300'
VAL_AUTO_100 = '0301'
VAL_AUTO_40 = '0302'

# mydata - bytearray object to calculate crc16 for
def crc16(mydata):
  crc = 0xffff
  
  for i in range(len(mydata)):
    crc = crc ^ mydata[i]
    for j in range(8): # All eight bits of the bytes
      if crc & 0x0001 != 0:
        crc = crc >> 1
        crc = crc ^ 0xA001
      else:
        crc =  crc >> 1

  crc = bytearray( [crc & 0xff, crc >> 8] )

  return crc

#All arguments expected as hex strings
def send_msg(slave, cmd, addr, command, ser, sleep_time=0.2):
  msg = bytearray()
  msg.append(int(slave, 16) )

  fc = int(cmd, 16)
  msg.append(fc)

  data = addr + command
  for i in range(int(len(data)/2)):
    hex_str = ''.join([ data[2*i], data[2*i+1] ])
    msg.append(int(hex_str,16))
  
  crc = crc16(msg)
  msg.append(crc[0])
  msg.append(crc[1])

  ser.write(msg)
  time.sleep(sleep_time)
  resp_len = ser.in_waiting
  resp = ser.read(resp_len)
  return resp

def set_temp(temp, ser):
  temp_eu = int(temp/PT100_SCALE_FACTOR)
  temp_str = hex(temp_eu)[2:]

  for i in range(4-len(temp_str)):
    temp_str = '0' + temp_str

  val = send_msg('01', CMD_WRITE_VAR_SINGLE, ADDR_SV, temp_str,  ser)
  
  return val

def start(ser):
  val = send_msg('01', CMD_WRITE_VAR_SINGLE, ADDR_COMMAND, VAL_START, ser)
  return val

def stop(ser):
  val = send_msg('01', CMD_WRITE_VAR_SINGLE, ADDR_COMMAND, VAL_STOP, ser)
  return val

def move_setup_1(ser):
  val = send_msg('01', CMD_WRITE_VAR_SINGLE, ADDR_COMMAND, VAL_SETUP_1, ser)
  return val

def soft_reset(ser):
  val = send_msg('01', CMD_WRITE_VAR_SINGLE, ADDR_COMMAND, VAL_SOFT_RESET, ser)
  return val

def auto_tune_100(ser):
  val = send_msg('01', CMD_WRITE_VAR_SINGLE, ADDR_COMMAND, VAL_AUTO_100, ser)
  return val

def auto_tune_40(ser):
  val = send_msg('01', CMD_WRITE_VAR_SINGLE, ADDR_COMMAND, VAL_AUTO_40, ser)
  return val

def auto_tune_0(ser):
  val = send_msg('01', CMD_WRITE_VAR_SINGLE, ADDR_COMMAND, VAL_AUTO_0, ser)
  return val

def set_pid(ser):
  move_setup_1(ser)
  val = send_msg('01', CMD_WRITE_VAR_SINGLE, ADDR_PID_ONOFF, VAL_PID, ser)
  soft_reset(ser)
  return val

def set_onoff(ser):
  move_setup_1(ser)
  val = send_msg('01', CMD_WRITE_VAR_SINGLE, ADDR_PID_ONOFF, VAL_ONOFF, ser)
  soft_reset(ser)
  return val

# Reads the current value of the process variable.
# Tuned for maximum reliable speed
def read_temp(ser):
  #0001 for length of bytes
  val = send_msg('01', CMD_READ_VAR_MULTIPLE, ADDR_PV, '0001', ser, 0.05)
  if len(val) == 0:
    return -300 
  if val[1] & int('80', 16) != 0:
    return -300 #Impossible temperature

  #Extract valid temperature in Celcius
  val = (val[3]*int('100',16) + val[4]) * PT100_SCALE_FACTOR

  return val

# Returns a valid pySerial object for interfacing with the e5cc @ 9600 Baud
#port_name - string representing name of port on system
def init_serial(port_name):
  ser = serial.Serial(port_name, 9600)
  ser.parity = serial.PARITY_EVEN
  return ser

