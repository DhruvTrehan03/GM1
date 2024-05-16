import serial
import time
import matplotlib.pyplot as plt

arduino = serial.Serial(port='COM8',  baudrate=115200, timeout=.1)
data = []
array = []


def write_read(x):
    arduino.write(bytes(x,  'utf-8'))
    time.sleep(0.05)
    data = arduino.readline()
    return  data



for k in range (100):
    value = (arduino.readline())
    if value != b'':
        value = str(value.strip(), 'utf-8')
        time.sleep(0.05)
        data = value.split(',')
        for i in range(len(data)):
            data[i] = int(data[i].split("=")[1])
        print(data)
        if data[1] == 1 and data[3] == 1:
            array.append([data[0],data[2]])
    #plt.plot(data)
print(array)
plt.plot(array[0])
plt.show()

