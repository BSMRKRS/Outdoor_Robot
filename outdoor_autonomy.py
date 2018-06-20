import RoboPiLib as RPL
import setup
import time

RPL.RoboPiInit("/dev/ttyAMA0",115200)

import sys, tty, termios, signal

######################
## Motor Establishment
######################

motorL = 0
motorR = 1

motorR_forward = 2000
motorR_backward = 1000
motorL_forward = 1000
motorL_backward = 2000

global mem
mem = [["start",0]]
global start
start = time.time()

try:
    RPL.pinMode(motorL,RPL.SERVO)
    RPL.servoWrite(motorL,1500)
    RPL.pinMode(motorR,RPL.SERVO)
    RPL.servoWrite(motorR,1500)
except:
    pass

######################
## Individual commands
######################
def stopAll():
    try:
        RPL.servoWrite(motorL,1500)
        RPL.servoWrite(motorR,1500)
    except:
        print "error except"
        pass

def forward():
    RPL.servoWrite(motorL,motorL_forward)
    RPL.servoWrite(motorR,motorR_forward)

def reverse():
    RPL.servoWrite(motorL,motorL_backward)
    RPL.servoWrite(motorR,motorR_backward)

def right():
    RPL.servoWrite(motorL,1460)#motorL_forward)
    RPL.servoWrite(motorR,1460)#motorR_backward)

def left():
    RPL.servoWrite(motorL,1540)#motorL_backward)
    RPL.servoWrite(motorR,1540)#motorR_forward)


def print_speed():
    print '--FORWARD: Left Motor: ', motorL_forward, ' Right Motor: ', motorR_forward, '\r'
    print '  BACKWARD: Left Motor: ', motorR_backward, ' Right Motor: ', motorL_backward, '\r'

def record_action(key):
    global mem
    global start
    if mem[-1][0] != key:
    mem.append([key, time.time() - start])

    fd = sys.stdin.fileno() # I don't know what this does
    old_settings = termios.tcgetattr(fd) # this records the existing console settings that are later changed with the tty.setraw... line so that they can be replaced when the loop ends

        ######################################
        ## Other motor commands should go here
        ######################################

def store_record():
    path = "/home/student/robotonomy/outdoor.txt"
    file = open(path, "w")
    global mem
    for i in range(0,len(mem)):
        file.write(str(mem[i][0])+","+str(mem[i][1])+"\r\n")
        file.close()
        print mem

def call_record():
    path = "/home/student/robotonomy/outdoor.txt"
    with open(path) as f:
        content = f.readlines()
        for i in range(0,len(content)-1):
            command = content[i].split(",")[0]
            start_command = float(content[i].split(",")[1])
            stop_command = float(content[i+1].split(",")[1])
            duration = stop_command - start_command
            drive_from_keys(command)
            print command, duration
            time.sleep(duration)

def interrupted(signum, frame): # this is the method called at the end of the alarm
    record_action('else')
    stopAll()

    signal.signal(signal.SIGALRM, interrupted) # this calls the 'interrupted' method when the alarm goes off
    tty.setraw(sys.stdin.fileno()) # this sets the style of the input

    print "Ready To Drive! Press * to quit.\r"
    ## the SHORT_TIMEOUT needs to be greater than the press delay on your keyboard
    ## on your computer, set the delay to 250 ms with `xset r rate 250 20`
    SHORT_TIMEOUT = 0.255 # number of seconds your want for timeout

def drive_from_keys(ch):
    if ch == 'w':
        forward()
        record_action(ch)
    elif ch == "a":
        left()
        record_action(ch)
    elif ch == "s":
        reverse()
        record_action(ch)
    elif ch == "d":
        right()
        record_action(ch)
    elif ch == "k":
        store_record()
    elif ch == "l":
        call_record()
    else:
        record_action(ch)
        stopAll()
while True:
    signal.setitimer(signal.ITIMER_REAL,SHORT_TIMEOUT) # this sets the alarm
    ch = sys.stdin.read(1) # this reads one character of input without requiring an enter keypress
    signal.setitimer(signal.ITIMER_REAL,0) # this turns off the alarm

    if ch == '*': # pressing the asterisk key kills the process
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings) # this resets the console settings
        break # this ends the loop

    else:
        drive_from_keys(ch)
