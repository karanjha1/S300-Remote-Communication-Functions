## Before running the script, install numpy and pyserial libraries

import numpy as np
import sys
import serial
import glob

## Function to identify all the serial ports available
def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


print(serial_ports())

## Based on observation, the probestation connected to the second COM port listed above
ser = serial.Serial(
    port=serial_ports()[1],  # Replace with your COM port
    baudrate=9600,  # Replace with your baud rate
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

## Functions to control the motion of the stage
def moveStage(ser,X=0,Y=0,Z=0):
    command = f":mov:rel:chuc 2 {X} {Y} {Z}"
    ser.write((command + '\r').encode())

def separate(ser):
    command = f":mov:sep 2"
    ser.write((command + '\r').encode())

def contact(ser):
    command = f":mov:cont 2"
    ser.write((command + '\r').encode())

## Functions to control the temperature of the stage
def thermalChuckDeactivate(ser):
    command = f":thermalchuck:deactivate"
    ser.write((command + '\r').encode())

def setTemperature(ser,newTemp=25.0,tempWindow=0.1):
    command = f":thermalchuck:temperature:settemp {newTemp}"
    ser.write((command + '\r').encode())
    command = f":thermalchuck:temperature:window 0.1"
    ser.write((command + '\r').encode())

def thermalChuckActivate(ser):
    command = f":thermalchuck:activate"
    ser.write((command + '\r').encode())

def stallForTemperature(ser):
    command = ":ther:stat?"
    ser. flushInput()
    ser.write((command + '\r').encode())
    ret = ser.readline().decode()
    while ret!= "AT TEMP":
        ser.write((command + '\r').encode())
        ret = ser.readline().decode()
        # print(ret)
    return

## Move the stage 1550um in Y direction 5 times (devices are separated by 1550um)
for i in range(5):
    separate(ser)
    moveStage(ser,Y=1550)
    contact(ser)


## Set temperature to 30.0 degrees
thermalChuckDeactivate(ser)
setTemperature(ser,newTemp=30.0,tempWindow=0.2)
thermalChuckActivate(ser)
stallForTemperature(ser)

## Close the serial connection
ser.close()