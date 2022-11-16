# %%
import serial
import time


with serial.Serial(port='COM7', baudrate=9600, timeout=1) as ser:
    time.sleep(1)
    # for j in range(10):
    # ser.write(b':measure:flux?\n')
    ser.write(b'*IDN?\n')
    message = ser.read_until()
    print(message)
    # meas = float(message.decode().strip('T;\n'))
    # print(meas)
# %%
