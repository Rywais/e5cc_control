#!/usr/bin/python3
SERIAL_PORT = '/dev/ttyUSB1'
LOWER_TEMP = 80
UPPER_TEMP = 120
STABILITY_TOL = 0.15
STABILITY_TIME = 15

import e5cc as e
import time as t
import serial
import numpy as np
import matplotlib.pyplot as plt

try:
  ser = e.init_serial(SERIAL_PORT)
except serial.serialutil.SerialException:
  print('Error initializing Serial Port')
  exit()

e.set_pid(ser)
e.set_temp(LOWER_TEMP, ser)

is_stable = False

#Wait for temperature to become stable about lower temperature value
while True:
  pv = e.read_temp(ser)
  if (LOWER_TEMP - STABILITY_TOL < pv) and (LOWER_TEMP + STABILITY_TOL > pv):
    stable_start = t.perf_counter()
    while (LOWER_TEMP - STABILITY_TOL < pv) and \
      (LOWER_TEMP + STABILITY_TOL > pv):

      pv = e.read_temp(ser)
      stable_time = t.perf_counter()
      if stable_time - stable_start > STABILITY_TIME:
        is_stable = True
        break
  
  if is_stable:
    break


#Ramp up the temperature and start measuring time
e.set_onoff(ser)
e.set_temp(UPPER_TEMP+5, ser)
ramp_start = t.perf_counter()
pv = LOWER_TEMP
temp_array = np.array([])
time_array = np.array([])

#Wait to reach upper temperature threshold
while (pv < UPPER_TEMP - 0.01):
  pv = e.read_temp(ser)
  temp_array = np.append(temp_array, pv)
  time_array = np.append(time_array, t.perf_counter() - ramp_start)
  

#Measure time elapsed and turn the temperature back down
ramp_finish = t.perf_counter()
e.set_pid(ser)
e.set_temp(UPPER_TEMP, ser)

print('Time to ramp temperature from %3.1f to %3.1f is %.2f seconds' \
  % (LOWER_TEMP,UPPER_TEMP,ramp_finish-ramp_start))

plt.plot(time_array,temp_array)
plt.ylabel('Temperature (deg Celcius)')
plt.xlabel('Time (Seconds)')
plt.show()
