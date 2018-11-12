###################################################################################
# Name: David M., Tristyn P., and Christian W.
###################################################################################

# set to 1 if testing on a computer if sensors arn't set up
TESTING = 1
# set to 0 if using Raspberry Pi
WINDOWS_OS = 1

if not TESTING:
    import RPi.GPIO as GPIO
if WINDOWS_OS:
    import winsound
else:
    import os
from time import sleep, time
from threading import Thread
from Tkinter import *
from random import randint

# number of elements to keep in sensor log before it discards oldest element
MAX_OUTPUT_LOG_SIZE = 50
# number of times the sensors record output per second (thus 10 would mean each sensor takes 10 samples/s)
POLL_RATE = 4
# period of time (in seconds) where sensor data is analyzed to determine if sensor has been tripped/set off
TIME_PERIOD_ANALYZE = .5
# percent of signals that must be positive within the time period for a sensor to be considered tripped
PERCENT_SIGNALS = 50


class MainGUI(Frame):
    # the constructor
    def __init__(self, parent):
        if TESTING:
            Frame.__init__(self, parent, bg="RoyalBlue1")
        else:
            Frame.__init__(self, parent, bg="RoyalBlue1", cursor="none")
        parent.attributes("-fullscreen", True)
        # boolean that indicates the security system is offline(the starting state) or online; toggled by the power button
        self.on = False
        self.alarm = False
        self.monitorWindow = True
        self.monitorDoor = True
        # create power button frame that toggles the system on/off
        self.powerButton = Button(self, text="System Off", font=("Arial", 32), bg="red", borderwidth=0,
                                  highlightthickness=0, activebackground="red", command=lambda: powerButton())
        self.powerButton.grid(row=2, column=3, sticky=N + S + E + W, columnspan=20, rowspan=10)
        # make GUI frames for the window and door, and have the default color be green, indicating they
        # have not been "broken" into to trip the alarm, otherwise, have frame flash red to signal the alarm being tripped
        self.windowFrame = Button(self, text="Window", font=("Arial", 26), bg="grey", activebackground="grey", command=lambda: deactivate("Window"))
        self.windowFrame.grid(row=20, column=5, sticky=N + S + E + W, columnspan=20, rowspan=10)
        self.doorFrame = Button(self, text="Door", font=("Arial", 26), bg="grey", activebackground="grey", command=lambda: deactivate("Door"))
        self.doorFrame.grid(row=20, column=30, sticky=N + S + E + W, columnspan=20, rowspan=10)

        # when powerButton frame is clicked, this function is called which toggles
        # the system state to on if the alarm is not active
        def powerButton():
            # don't allow state to be changed if alarm active
            if self.alarm:
                return
            if self.on:
                self.powerButton.configure(bg="red", activebackground="red", text="System Off")
                self.on = 0
                # set sensor frames to grey if they are not disabled
                if self.monitorWindow:
                    self.windowFrame.configure(bg="grey")
                if self.monitorDoor:
                    self.doorFrame.configure(bg="grey")
                for sensor in sensorList:
                    if self.monitorWindow and sensor.location == "Window":
                        sensor.GUIref.configure(bg="grey")
                    elif self.monitorDoor and sensor.location == "Door":
                        sensor.GUIref.configure(bg="grey")
            else:
                self.powerButton.configure(bg="green", activebackground="green", text="System On")
                self.on = 1

        # deactivate the set of sensors and set frames to yellow, otherwise toggle back
        # to active state if it was deactivated
        def deactivate(object):
            # if password is not correct (in this case "9999") or if alarm is on terminate function
            if self.display["text"] != "9999" or self.alarm:
                return
            # otherwise allow user to toggle the sensor state and wipe display frame
            self.display["text"] = ""
            if object == "Window":
                if self.monitorWindow:
                    self.windowFrame.configure(bg="yellow", activebackground="yellow")
                    for sensor in sensorList:
                        if sensor.location == "Window":
                            sensor.GUIref.configure(bg="yellow")
                    self.monitorWindow = 0
                else:
                    # if system is on, set window frames to green and wipe outputLog
                    if self.on:
                        self.windowFrame.configure(bg="green", activebackground="green")
                        for sensor in sensorList:
                            if sensor.location == object:
                                sensor.outputLog = [0]
                                sensor.GUIref.configure(bg="green")
                        self.monitorWindow = 1
                    # if system is off set window frames to grey
                    elif self.off:
                        self.windowFrame.configure(bg="grey", activebackground="grey")
                        for sensor in sensorList:
                            if sensor.location == object:
                                sensor.GUIref.configure(bg="grey")
                        self.monitorWindow = 1
            else:
                if object == "Door":
                    if self.monitorDoor:
                        self.doorFrame.configure(bg="yellow", activebackground="yellow")
                        for sensor in sensorList:
                            if sensor.location == object:
                                sensor.GUIref.configure(bg="yellow")
                        self.monitorDoor = 0
                    else:
                        # if system is on, set window frames to green and wipe outputLog
                        if self.on:
                            self.doorFrame.configure(bg="green", activebackground="green")
                            for sensor in sensorList:
                                if sensor.location == object:
                                    sensor.outputLog = [0]
                                    sensor.GUIref.configure(bg="green")
                            self.monitorDoor = 1
                        elif self.off:
                            self.doorFrame.configure(bg="grey", activebackground="grey")
                            for sensor in sensorList:
                                if sensor.location == object:
                                    sensor.GUIref.configure(bg="grey")
                            self.monitorDoor = 1


        # set up the rest of the GUI
        self.setupGUI()

    def setupGUI(self):
        # Rasp Pi screen dimensions: 800 x 480 (pixels)
        # create a 100 by 60 grid (preserving the 5:3 aspect ratio)
        SCREEN_WIDTH = 100
        SCREEN_HEIGHT = 60
        for col in range(SCREEN_WIDTH):
            Grid.columnconfigure(self, col, weight=1)
        for row in range(SCREEN_HEIGHT):
            Grid.rowconfigure(self, row, weight=1)

        # set up frames for each window and door sensor, where green indicates
        # their default state, whereas red indicates the sensor being set off
        for i in range(len(sensorDictFormat['Window'])):
            sensor = sensorDictFormat['Window'][i]
            a = Label(self, text=sensorDict['Window'][sensor].type + " Sensor", font=("Arial", 18),
                      bg="grey", relief="ridge")
            a.grid(row=int(35 + 12 * i), column=5, sticky=N + S + E + W, columnspan=20, rowspan=12)
            sensorDict['Window'][sensor].GUIref = a
        for i in range(len(sensorDictFormat['Door'])):
            sensor = sensorDictFormat['Door'][i]
            a = Label(self, text=sensorDict['Door'][sensor].type + " Sensor", font=("Arial", 18),
                                            bg="grey", relief="ridge")
            a.grid(row=int(35 + 8 * i), column=30, sticky=N + S + E + W, columnspan=20, rowspan=8)
            sensorDict['Door'][sensor].GUIref = a

        # create borders surrounding sensor status windows
        # format: row, column, column span, row span, gridded by 5's
        sizeSpecs = [[15, 0, 55, 5], [15, 0, 5, 45], [59, 0, 55, 1],
                    [30, 0, 55, 5], [15, 25, 5, 45], [15, 50, 5, 45]]
        for i in range(6):
            windowBorder = Label(self, bg="black")
            windowBorder.grid(row=sizeSpecs[i][0], column=sizeSpecs[i][1], sticky=N + S + E + W,
                                  columnspan=sizeSpecs[i][2], rowspan=sizeSpecs[i][3])

        # the display for the keypad
        self.display = Label(self, text="", bg="grey", font=("Arial", 25))
        self.display.grid(row=15, column=65, columnspan=30, rowspan=7,
                          sticky=E + W + N + S)

        # the button layout for keypad
        # 7 8 9
        # 4 5 6
        # 1 2 3
        # < 0

        # create the keypad
        key = Button(self, text="7", font=("Arial", 18), bg="purple", activebackground="purple",
                     command=lambda: self.keyPress("7"))
        key.grid(row=22 + 10 * 0, column=65 + 10 * 0, sticky=N + S + E + W, columnspan=10, rowspan=10)
        key = Button(self, text="8", font=("Arial", 18), bg="purple", activebackground="purple",
                     command=lambda: self.keyPress("8"))
        key.grid(row=22 + 10 * 0, column=65 + 10 * 1, sticky=N + S + E + W, columnspan=10, rowspan=10)
        key = Button(self, text="9", font=("Arial", 18), bg="purple", activebackground="purple",
                     command=lambda: self.keyPress("9"))
        key.grid(row=22 + 10 * 0, column=65 + 10 * 2, sticky=N + S + E + W, columnspan=10, rowspan=10)
        key = Button(self, text="4", font=("Arial", 18), bg="purple", activebackground="purple",
                     command=lambda: self.keyPress("4"))
        key.grid(row=22 + 10 * 1, column=65 + 10 * 0, sticky=N + S + E + W, columnspan=10, rowspan=10)
        key = Button(self, text="5", font=("Arial", 18), bg="purple", activebackground="purple",
                     command=lambda: self.keyPress("5"))
        key.grid(row=22 + 10 * 1, column=65 + 10 * 1, sticky=N + S + E + W, columnspan=10, rowspan=10)
        key = Button(self, text="6", font=("Arial", 18), bg="purple", activebackground="purple",
                     command=lambda: self.keyPress("6"))
        key.grid(row=22 + 10 * 1, column=65 + 10 * 2, sticky=N + S + E + W, columnspan=10, rowspan=10)
        key = Button(self, text="1", font=("Arial", 18), bg="purple", activebackground="purple",
                     command=lambda: self.keyPress("1"))
        key.grid(row=22 + 10 * 2, column=65 + 10 * 0, sticky=N + S + E + W, columnspan=10, rowspan=10)
        key = Button(self, text="2", font=("Arial", 18), bg="purple", activebackground="purple",
                     command=lambda: self.keyPress("2"))
        key.grid(row=22 + 10 * 2, column=65 + 10 * 1, sticky=N + S + E + W, columnspan=10, rowspan=10)
        key = Button(self, text="3", font=("Arial", 18), bg="purple", activebackground="purple",
                     command=lambda: self.keyPress("3"))
        key.grid(row=22 + 10 * 2, column=65 + 10 * 2, sticky=N + S + E + W, columnspan=10, rowspan=10)
        key = Button(self, text="<", font=("Arial", 18), bg="purple", activebackground="purple",
                     command=lambda: self.keyPress("<"))
        key.grid(row=22 + 10 * 3, column=65 + 10 * 0, sticky=N + S + E + W, columnspan=10, rowspan=10)
        key = Button(self, text="0", font=("Arial", 18), bg="purple", activebackground="purple",
                     command=lambda: self.keyPress("0"))
        key.grid(row=22 + 10 * 3, column=65 + 10 * 1, sticky=N + S + E + W, columnspan=10, rowspan=10)
        key = Button(self, text="C", font=("Arial", 18), bg="purple", activebackground="purple",
                     command=lambda: self.keyPress("C"))
        key.grid(row=22 + 10 * 3, column=65 + 10 * 2, sticky=N + S + E + W, columnspan=10, rowspan=10)

        # pack the GUI
        self.pack(fill=BOTH, expand=1)

        # start the thread that continually analyzes sensor output
        Thread(target=self.determineGUIstate).start()

    # append key character to display and set both alarm and system to off if password is correct
    def keyPress(self, char):
        # delete last character
        if char == "<":
            self.display["text"] = self.display["text"][:-1]
        # clear the text
        elif char == "C":
            self.display["text"] = ""
        elif len(self.display["text"]) < 4:
            self.display["text"] += char
        if self.display["text"] == "1111":
            self.display["text"] = ""
            self.alarm = 0
            self.on = 0
            self.powerButton.configure(bg="red", activebackground="red", text="System Off")
            if self.monitorWindow:
                self.windowFrame.configure(bg="grey")
            if self.monitorDoor:
                self.doorFrame.configure(bg="grey")
            for sensor in sensorList:
                if self.monitorWindow and sensor.location == "Window":
                    sensor.GUIref.configure(bg="grey")
                elif self.monitorDoor and sensor.location == "Door":
                    sensor.GUIref.configure(bg="grey")

    # analyze sensor output and change the state of frames/windows accordingly when system is live
    def determineGUIstate(self):
        dataLogsWiped = 0
        while 1:
            # system off state or alarm state
            if not self.on or self.alarm:
                dataLogsWiped = 0
                # keep sleeping until alarm is off and power button is pressed to turn system on
                sleep(.25)

            # if system is on and no alarm is triggered, keep track of sensor out and react accordingly
            elif self.on and not self.alarm:
                # wipe sensor data logs if system is turned on for the first time
                if dataLogsWiped == 0:
                    for sensor in sensorList:
                        sensor.outputLog = [0]
                    dataLogsWiped = 1
                    # set every window to green if it is not disabled
                    if self.monitorWindow:
                        self.windowFrame.configure(bg="green")
                    if self.monitorDoor:
                        self.doorFrame.configure(bg="green")
                    for sensor in sensorList:
                        if self.monitorWindow and sensor.location == "Window":
                            sensor.GUIref.configure(bg="green")
                        elif self.monitorDoor and sensor.location == "Door":
                            sensor.GUIref.configure(bg="green")

                # initialize counters to keep track of how many sensors have been set off for door and window
                doorSensorsTripped = int(0)
                winSensorsTripped = int(0)
                for sensor in sensorList:
                    # desired number of samples needed to determine if sensor has been tripped
                    n = int(TIME_PERIOD_ANALYZE * POLL_RATE)
                    # break out of loop if there is not enough samples of data
                    if len(sensor.outputLog) < n:
                        break
                    # if the sensor is disabled, continue to the next sensor in for loop
                    if (sensor.location == "Window" and not self.monitorWindow) or (sensor.location == "Door" and not self.monitorDoor):
                        continue
                    # if the proportion of the positive samples for the last n samples is greater than the defined
                    #  threshold, the sensor will be tripped, turning the color of that sensor frame red
                    avg = sum(sensor.outputLog[-n:]) / float(n)
                    if TESTING:
                        print('sensor loc: {} sensor type: {} avg: {} output: {}'.format(
                            sensor.location, sensor.type, avg, sensor.outputLog))
                    if avg < (float(PERCENT_SIGNALS) / 100):
                        sensor.GUIref.configure(bg="green")
                    else:
                        sensor.GUIref.configure(bg="red")
                        if sensor.location == "Door":
                            doorSensorsTripped += 1
                        else:
                            winSensorsTripped += 1
                # if more than 1 sensor is tripped for the door and/or window, make the door and/or
                # window flash red and change alarm state to 1
                if doorSensorsTripped > 1 and winSensorsTripped > 1:
                    self.alarm = 1
                    Thread(target=self.frameFlashRed, args=[self.windowFrame]).start()
                    Thread(target=self.frameFlashRed, args=[self.doorFrame]).start()
                    Thread(target=self.playSiren).start()
                elif doorSensorsTripped > 1:
                    self.alarm = 1
                    Thread(target=self.frameFlashRed, args=[self.doorFrame]).start()
                    Thread(target=self.playSiren).start()
                elif winSensorsTripped > 1:
                    self.alarm = 1
                    Thread(target=self.frameFlashRed, args=[self.windowFrame]).start()
                    Thread(target=self.playSiren).start()

            # sleep for every poll rate interval to give sensors time to generate a new data point
            sleep(1 / float(POLL_RATE))

    # make the inputted frame flash red during alarm state
    def frameFlashRed(self, ref):
        while self.alarm:
            ref.configure(bg="red")
            sleep(.5)
            ref.configure(bg="black")
            sleep(.2)

        ref.configure(bg="grey")

    # play siren sound while the alarm is on
    # ensure that siren.wav file is in same directory
    def playSiren(self):
        while self.alarm:
            if WINDOWS_OS:
                winsound.PlaySound('siren.wav', winsound.SND_FILENAME)
            else:
                os.system("aplay siren.wav")

class Sensor(object):
    def __init__(self, name, type, location, inputPin, outputPin):
        self.name = name
        self.type = type
        self.location = location
        self.inputPin = inputPin
        self.outputPin = outputPin
        self.outputLog = []
        self.GUIref = 0

        # setup input pin
        if not TESTING:
            GPIO.setup(inputPin, GPIO.IN, GPIO.PUD_DOWN)


def setupSensors():
    global sensorDictFormat
    # dictionaries containing information regarding the sensors
    sensorSpecs = {'dV': {'type': 'Vibration', 'location': 'Door', 'inputPin': 17, 'outputPin': 16},
                   'dMot': {'type': 'Motion', 'location': 'Door', 'inputPin': 12, 'outputPin': 13},
                   'dMag': {'type': 'Magnetic', 'location': 'Door', 'inputPin': 23, 'outputPin': 22},
                   'wV': {'type': 'Vibration', 'location': 'Window', 'inputPin': 27, 'outputPin': 26},
                   'wMot': {'type': 'Motion', 'location': 'Window', 'inputPin': 25, 'outputPin': 24}}
    sensorDictFormat = {'Door': ['Vibration', 'Motion', 'Magnetic'], 'Window': ['Vibration', 'Motion']}

    # make a list of the sensors by accessing the keys of the sensor dictionary
    sensorList = sensorSpecs.keys()
    sensorDict = {}
    for key in (sensorDictFormat.keys()):
        sensorDict[key] = {sensorDictFormat[key][i]: 0 for i in range(len(sensorDictFormat[key]))}

    # use Broadcom pin mode
    if not TESTING:
        GPIO.setmode(GPIO.BCM)

    # instantiate each sensor in the list and reassign each element in the list to the new object,
    # thereby making a list of instance references
    i = 0
    for sensor in sensorList:
        s = Sensor(sensor, sensorSpecs[sensor]['type'], sensorSpecs[sensor]['location'],
                   sensorSpecs[sensor]['inputPin'], sensorSpecs[sensor]['outputPin'])
        sensorDict[sensorSpecs[sensor]['location']][sensorSpecs[sensor]['type']] = s
        sensorList[i] = s
        i += 1

    return sensorList, sensorDict


# monitor sensors/log output
def monitorSensors():
    global sensorList, sensorDict
    # run the setup sensors function which instantiates them
    output = setupSensors()
    sensorList = output[0]
    sensorDict = output[1]

    # if testing without sensors set up, terminate function so there are no attempts to get sensor input
    if TESTING:
        return

    while 1:
        for i in range(len(sensorList)):
            # delete first element in outputLog list if the size is over desired threshold
            if len(sensorList[i].outputLog) > MAX_OUTPUT_LOG_SIZE:
                sensorList[i].outputLog.pop(0)
            if GPIO.input(sensorList[i].inputPin):
                # add 1 to outputLog if sensor is tripped
                sensorList[i].outputLog.append(1)
            else:
                # add 0 to outputLog if sensor is not triggered
                sensorList[i].outputLog.append(0)
        sleep(1 / float(POLL_RATE))

        # print the output log of each sensor every defined interval
        counter = 0
        # how frequently (in seconds) output should be printed out
        intervalToPrintOutput = 1
        if TESTING:
            counter += 1
            if counter >= (POLL_RATE * intervalToPrintOutput):
                for i in range(len(sensorList)):
                    print("Sensor: {}, Data: {}".format(sensorList[i].name, sensorList[i].outputLog))
                counter = 0


def runGUI():
    # create the window
    window = Tk()
    # set the window title
    window.title("Security System")
    # generate the GUI
    p = MainGUI(window)
    # display the GUI and wait for user interaction
    window.mainloop()


# generate random sensor output data for testing purposes
def testingGenerateSensorData():
    while 1:
        for i in range(len(sensorList)):
            if len(sensorList[i].outputLog) > MAX_OUTPUT_LOG_SIZE:
                sensorList[i].outputLog.pop(0)
            if randint(0, 3) < 1:
                sensorList[i].outputLog.append(1)
            else:
                sensorList[i].outputLog.append(0)
            #sensorList[i].outputLog.append(1)
        sleep(.5)

# function that calls for multiple functions to run in seperate threads,
# resulting in the functions to run in parallel of each other
def runThreads():
    if __name__ == '__main__':
        Thread(target=monitorSensors).start()
        sleep(.05)
        Thread(target=runGUI).start()
        if TESTING:
            Thread(target=testingGenerateSensorData).start()

runThreads()



