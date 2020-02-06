import cv2
import random
import numpy as np
import curses
import time
import RPi.GPIO as GPIO

# For keyboard input
cur = curses.initscr()

# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture(0)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# For the record... ;)
def resetRecordedFile():
    fourcc = cv2.VideoWriter_fourcc(*'XVID') 
    return cv2.VideoWriter('test.avi', fourcc, 20, (640,480))
    
# Negative filter function
def apply_invert(frame):
    return cv2.bitwise_not(frame)

# Grayscale filter function
def apply_grayScale(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

def artifact(frame):
    return frame
# Initialising some values
record = False
out = resetRecordedFile()
fWidth = 0
cur.nodelay(1)
captureDuration = 10
startTime = 0

# Check if camera opened successfully
if (cap.isOpened()== False): 
    print("Error opening video stream or file")
else:
    ret, frame = cap.read()
    height, width, channels = frame.shape
    
# Read until video is completed
while(cap.isOpened()):
    if GPIO.input(10) == GPIO.HIGH:
        print('ayyyy')
    
    # imshow won't display without this
    cv2.waitKey(1)
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    if ret == True:
        
        if record == True:
            if time.time() - startTime < captureDuration:    
                out.write(frame)
            else:
                record = False
                print('Recording done, press A to playback \r')
        # Will modify later
        for y in range(0, height-1):
            if random.randint(0,100) >= 75:
                c = random.randint(0,255)
                frame[y, random.randint(fWidth-1, fWidth+1)] = [c, c ,c]
        
        # Display the resulting frame
        cv2.imshow('Frame', apply_grayScale(frame))
        
        fWidth += 1
        
        if fWidth >= width-1:
            fWidth = 0
        
        try:
            char = cur.getch()
            if char > 0:
                if chr(char) == 'z':
                    record = not record
                    print(' Recording has started for : ', captureDuration, ' seconds\r')
                    if record == False:
                        out.release()
                    else:
                        out = resetRecordedFile()
                        startTime = time.time()
                if chr(char) == 'a':
                    cap = cv2.VideoCapture('test.avi')
                elif chr(char) == 'q':
                    break
                
        except KeyboardInterrupt:
            curses.endwin()
            
    else:
        # We reload the capture
        cap = cv2.VideoCapture(0)
        # Loop breaker is here by default,
        # but we need to restart showing the camera feed instead 
        #break
 
# Closes keyboard interface
curses.endwin()
# When everything done, release the video capture object
cap.release()
# Release the output object in case something happens
out.release() 
# Closes all the frames
cv2.destroyAllWindows()
