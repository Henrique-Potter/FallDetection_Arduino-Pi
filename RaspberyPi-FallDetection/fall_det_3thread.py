debug = 1
from picamera.array import PiRGBArray
from threading import Thread
from picamera import PiCamera
import RPi.GPIO as GPIO
import Queue
import time
import cv2

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)

readyContour = Queue.Queue()
ggframes = Queue.Queue()



def applyGaussian(frame,ggframes):
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  if useGaussian:
    gray = cv2.GaussianBlur(gray, (gaussianPixels, gaussianPixels), 0)
  ggframes.put(gray)

def getFrameDif(firstFrame,gray,readyContour):
  frameDelta = cv2.absdiff(firstFrame, gray)
  thresh = cv2.threshold(frameDelta, thresholdLimit, 255, cv2.THRESH_BINARY)[1]
  thresh = cv2.dilate(thresh, None, iterations=dilationPixels) # dilate thresh
  _, contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #find contours
  readyContour.put(contours)
  
def convertFrame (frame):
  r = 750.0 / frame.shape[1]
  dim = (750, int(frame.shape[0] * r))
  frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
  return frame

# Video or camera
camera = PiCamera()
camera.vflip = True
camera.resolution = (1024, 864)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(1024, 864))

time.sleep(1.0)

firstFrame = None
start = time.time()
i = 0
lastH = [0]*100
lastW = [0]*100
boxPosition = [0]*100

# Global params
widthRatio = 1.40
minArea = 40*40
thresholdLimit = 20
dilationPixels = 20 # 10
useGaussian = 1
gaussianPixels = 31
contours=[]
upDateFrame=0
firstTime=True
fallState = ""
redBox = (0,0,255)
greenBox = (124,252,0)
boxColor=redBox

# looping trought each frame in video stream
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
  
  detectStatus = "Empty"
  frame = frame.array
  frame = convertFrame(frame)
  
  if firstTime==True:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if useGaussian:
      gray = cv2.GaussianBlur(gray, (gaussianPixels, gaussianPixels), 0)
    firstTime=False
  
  #Starting a thread to calculate gaussian application
  gthread = Thread(target = applyGaussian,args = (frame,ggframes))
  if gthread.isAlive()==False:
    gthread.start()
  
  #Get result if avaliable
  if ggframes.empty()==False:
    gray=ggframes.get_nowait()


  if firstFrame is None:
    rawCapture.truncate(0)
    time.sleep(1.0) # let camera autofocus + autosaturation settle
    firstFrame = gray
    continue

  #Thread responsible to calculate frame by frame difference
  thread = Thread(target = getFrameDif, args = (firstFrame,gray,readyContour))
  if thread.isAlive()==False:
    thread.start()
  
  if readyContour.empty()==False:
    contours=readyContour.get_nowait()

  if not contours:
    GPIO.output(20,False)
  
  for contour in contours:
    if cv2.contourArea(contour) < minArea:
      continue

    #Drawing rectangle over contour
    (x, y, w, h) = cv2.boundingRect(contour)
    cv2.rectangle(frame, (x, y), (x + w, y + h), boxColor, 2)
    boxPosition[i] = x+y
    

    if w > h*widthRatio:
      GPIO.output(20,True)
      fallState = "Alarm!"
      boxColor=redBox
      print "Alarm: " + format(time.time())
    else:
      fallState = ""
      boxColor = greenBox


    lastW[i] = w
    lastH[i] = h
    #cv2.putText(frame,"{}".format(cv2.contourArea(contour)), (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1)
    cv2.putText(frame, "{}".format(i), (x, y+22), cv2.FONT_HERSHEY_SIMPLEX, 0.8, boxColor, 1)
    cv2.putText(frame, "{}".format(fallState), (x+22, y+22), cv2.FONT_HERSHEY_SIMPLEX, 0.8, boxColor, 1)
    detectStatus = "Ok"
    i+=1
    
  #Hud + fps
  if debug:
    end = time.time()
    seconds = end - start
    fps  = round((1 / seconds), 1)
    start = time.time()
    cv2.putText(frame, "Detect: {}".format(detectStatus), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 1)
    cv2.putText(frame, "FPS: {}".format(fps), (400, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 1)

  cv2.imshow("Feed", frame)
  
  i = 0
  
  rawCapture.truncate(0)
  upDateFrame=+1
  key = cv2.waitKey(1) & 0xFF
  if key == ord("q"):
    break
  if key == ord("n"):
    firstFrame = None
  
    
# Release resources
GPIO.cleanup()
camera.release()
cv2.destroyAllWindows()
