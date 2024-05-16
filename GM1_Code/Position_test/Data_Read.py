import serial
import time
import matplotlib.pyplot as plt

arduino = serial.Serial(port='COM3',  baudrate=115200, timeout=.1)
data = []

def write_read(x):
    arduino.write(bytes(x,  'utf-8'))
    time.sleep(0.05)
    data = arduino.readline()
    return  data



while True:
    value = (arduino.readline())
    if value != b'':
        print(str(value.strip(), 'utf-8'))
        data.append(str(value, 'utf-8'))
        time.sleep(0.05)
    #plt.plot(data)
    #plt.show()
