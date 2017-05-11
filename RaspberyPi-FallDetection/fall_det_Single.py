debug = 1
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import RPi.GPIO as GPIO
import time

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)


def convertFrame (frame):
  r = 750.0 / frame.shape[1]
  dim = (750, int(frame.shape[0] * r))
  frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  if useGaussian:
    gray = cv2.GaussianBlur(gray, (gaussianPixels, gaussianPixels), 0)
  return frame, gray


# Video or camera
camera = PiCamera()
camera.vflip = True
camera.resolution = (1024, 860)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(1024, 860))

time.sleep(1.0)

firstFrame = None
start = time.time()
i = 0
lastH = [0]*100
lastW = [0]*100


# Detect parameters
minArea = 30*30
thresholdLimit = 20
dilationPixels = 20 # 10
useGaussian = 1
gaussianPixels = 31

upDateFrame=0

# loop for each frame in video
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
  
  detectStatus = "Empty"
  frame = frame.array
  frame, gray = convertFrame(frame)

 

  if firstFrame is None:
    rawCapture.truncate(0)
    time.sleep(1.0) # let camera autofocus + autosaturation settle
    firstFrame = gray
    continue

  # difference between the current frame and firstFrame
  frameDelta = cv2.absdiff(firstFrame, gray)
  thresh = cv2.threshold(frameDelta, thresholdLimit, 255, cv2.THRESH_BINARY)[1]
  thresh = cv2.dilate(thresh, None, iterations=dilationPixels) # dilate thresh
  _, contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #find contours
 
  for contour in contours:
    if cv2.contourArea(contour) < minArea:
      continue

    # Drawing rect over contour
    (x, y, w, h) = cv2.boundingRect(contour)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
    
    if w > lastW[i]*1.40:
      GPIO.output(20,True)
      print "Alarm: " + format(time.time())
    else:
      GPIO.output(20,False)

    lastW[i] = w
    lastH[i] = h
    #cv2.putText(frame,"{}".format(cv2.contourArea(contour)), (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1)
    cv2.putText(frame, "{}".format(i), (x, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 1)
    detectStatus = "Ok"
    i+=1
  # Hud + fps
  if debug:
    end = time.time()
    seconds = end - start
    fps  = round((1 / seconds), 1)
    start = time.time()

    cv2.putText(frame, "Detect: {}".format(detectStatus), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 1)
    cv2.putText(frame, "FPS: {}".format(fps), (400, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 1)
    #cv2.imshow("frameDelta", frameDelta)
    #cv2.imshow("Thresh", thresh)
    #cv2.imshow("firstFrame", firstFrame)

  cv2.imshow("Feed", frame)
  
  i = 0
  
  rawCapture.truncate(0)
  upDateFrame=+1
  key = cv2.waitKey(1) & 0xFF
  if key == ord("q"):
    GPIO.cleanup()
    break
  if key == ord("n"):
    firstFrame = None
##  if upDateFrame == 10:
##    upDateFrame=0
##    firstFrame = None
    

# Release and destroy
GPIO.cleanup()
camera.release()
cv2.destroyAllWindows()
