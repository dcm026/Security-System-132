###################################################################################
# Name: David M., Tristyn P., and Christian W.
# Date:
# Description:
###################################################################################

import RPi.GPIO as GPIO
from time import sleep, time
from threading import Thread
# import pygame
# from array import array
# import math



MAX_OUTPUT_LOG_SIZE = 20 # number of elements to keep in sensor log before it discards oldest element
POLL_RATE = 4 # number of times the sensors record output per second (thus 10 would mean each sensor takes 10 samples/s)

class Sensor(object):

    def __init__(self, name, type, location, inputPin, outputPin):
        self.name = name
        self.type = type
        self.location = location
        self.inputPin = inputPin
        self.outputPin = outputPin
        self.outputLog = []

        # setup input pin
        GPIO.setup(inputPin, GPIO.IN, GPIO.PUD_DOWN)


def setup_sensors():
    # a dictionary of dictionaries following the format...
    # where dV is the name of the instance reference with d standing for door, and V standing for vibration
    # (as the type is a vibration sensor)
    sensor_dict = {'dV': {'type': 'vibration', 'location': 'door', 'inputPin': 27, 'outputPin': 26},
                   'dMot': {'type': 'motion', 'location': 'door', 'inputPin': 25, 'outputPin': 24},
                   'dMag': {'type': 'magnetic', 'location': 'door', 'inputPin': 23, 'outputPin': 22},
                   'wV': {'type': 'vibration', 'location': 'window', 'inputPin': 17, 'outputPin': 16},
                   'wMot': {'type': 'motion', 'location': 'window', 'inputPin': 13, 'outputPin': 12}}
    sensor_list = sensor_dict.keys()

    # use Broadcom pin mode
    GPIO.setmode(GPIO.BCM)

    i = 0
    for sensor in sensor_list:
        sensor_list[i] = Sensor(sensor, sensor_dict[sensor]['type'], sensor_dict[sensor]['location'], sensor_dict[sensor]['inputPin'], sensor_dict[sensor]['outputPin'])
        i += 1

    return sensor_list


# monitor sensors/log output
def monitor_sensors():
    global sensor_list
    sensor_list = setup_sensors()
    #for i in range(len(sensor_list)):


    while 1:
        for i in range(len(sensor_list)):

            if GPIO.input(sensor_list[i].inputPin):
                if len(sensor_list[i].outputLog) > MAX_OUTPUT_LOG_SIZE:
                    sensor_list[i].outputLog.pop(0) # delete first element in outputLog list
                sensor_list[i].outputLog.append(1) # add 1 to outputLog if sensor is tripped
            else:
                if len(sensor_list[i].outputLog) > MAX_OUTPUT_LOG_SIZE:
                    sensor_list[i].outputLog.pop(0) # delete first element in outputLog list
                sensor_list[i].outputLog.append(0) # add 0 to outputLog if sensor is not triggered
        sleep(1 / float(POLL_RATE))

        # to test a single sensor
        # if GPIO.input(27):
        #     print
        #     'On'
        # else:
        #     print
        #     'OFF!'
        # sleep(.1)


def GUI_control():
    # PLACEHOLDER
    sleep(1)

    counter = 0
    while 1:
        print(counter)
        for i in range(len(sensor_list)):
            print("Sensor: {}, Data: {}".format(sensor_list[i].name, sensor_list[i].outputLog))
        sleep(1)
        counter += 1


def run_parallel_threads():
    if __name__ == '__main__':
        Thread(target=monitor_sensors).start()
        Thread(target=GUI_control).start()



run_parallel_threads()


# setup input pins
#GPIO.setup(27, GPIO.IN, GPIO.PUD_DOWN)

# setup output pins
# GPIO.setup(pinNum, GPIO.OUT)




