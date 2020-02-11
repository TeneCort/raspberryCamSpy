import cv2
import random
import numpy as np
import time
import RPi.GPIO as GPIO
import vlc

# Initialising a full screen window
cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture(0)

# GPIO initialisation
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# VLC player initialisation
scream = vlc.MediaPlayer("/home/pi/Desktop/camspy/scream.mp3")

# For the record... ;)
def resetRecordedFile():
    fourcc = cv2.VideoWriter_fourcc(*'XVID') 
    return cv2.VideoWriter('/home/pi/Desktop/camspy/recording.avi', fourcc, 20, (640,480))
    
# Negative filter function
def apply_invert(frame):
    return cv2.bitwise_not(frame)

# Grayscale filter function
def apply_grayScale(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Button pressed callback
def recordPressed(channel):
    print('Starting record \r')

def recordPlayPressed(channel):
    print('Playing record \r')

# TODO: Relocate artifact code inside this function to cleanup 
def artifact(frame):
    return frame

def playSound():
    scream.stop()
    scream.pause()
    scream.play()

# Initialising some values
record = False
playBack = False
out = resetRecordedFile()
fWidth = 0
captureDuration = 10
startTime = 0
GPIO.add_event_detect(10, GPIO.RISING, callback = recordPressed)
GPIO.add_event_detect(12, GPIO.RISING, callback = recordPlayPressed)

# Check if camera opened successfully
if (cap.isOpened()== False): 
    print("Error opening video stream or file")
else:
    ret, frame = cap.read()
    height, width, channels = frame.shape
    
# Read until video is completed
while(cap.isOpened()):
     # imshow won't display without this
    key = cv2.waitKey(1)
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
        cv2.imshow('window', apply_grayScale(frame))
        
        fWidth += 1
        
        if fWidth >= width-1:
            fWidth = 0
        
        if playBack == True:
            cv2.waitKey(50)
        
        try:
            if key == ord('z'):
                record = not record
                print(' Recording has started for : ', captureDuration, ' seconds\r')
                if record == False:
                    out.release()
                else:
                    out = resetRecordedFile()
                    startTime = time.time()
            if key == ord('a'):
                playBack = True
                cap = cv2.VideoCapture('/home/pi/Desktop/camspy/recording.avi')
            if key == ord('t'):
                playSound()
            elif key == ord('q'):
                break
                
        except KeyboardInterrupt:
            break
            
    else:
        # We reload the capture
        cap = cv2.VideoCapture(0)
        # usually this condition is read when the playback has ended, thus we switch it to false
        playBack = False
        # Loop breaker is here by default,
        # but we need to restart showing the camera feed instead 
        #break
 
# Cleans the GPIOs 
GPIO.cleanup()
# When everything done, release the video capture object
cap.release()
# Release the output object in case something happens
out.release() 
# Closes all the frames
cv2.destroyAllWindows()
