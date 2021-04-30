"""  OctoWS2811 movie2serial.pde - Transmit video data to 1 or more
      Teensy 3.0 boards running OctoWS2811 VideoDisplay.ino
    http:#www.pjrc.com/teensy/td_libs_OctoWS2811.html
    Copyright (c) 2018 Paul Stoffregen, PJRC.COM, LLC

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""

import math, time, cv2, queue,  random, numpy as np
from serial import Serial
from cv2 import cv2
from threading import Thread
from os import listdir
from os.path import isfile, join, dirname, realpath

gamma = 1.7

numPorts=0
maxPorts=24
portNames = ["COM6","COM7"]

ledSerial = [None] * maxPorts
ledArea = [None] * maxPorts
ledLayout = [None] * maxPorts
ledImage = [None] * maxPorts
gammatable = [None] * 256
errorCount = 0
framerate = 0

movieQueue = queue.Queue()

stdMvList = []

cwd = dirname(realpath(__file__))

class Rectangle:
  def __init__(self,x,y,width,height):
    self.x = x
    self.y = y
    self.width = width
    self.height = height

def setupLED():
  global movieQueue, errorCount, stdMvList
 
  for pN in portNames:
    _serialConfigure(pN)
  if (errorCount > 0):
    exit()
  for i in range(256):
    gammatable[i] = math.pow(i / 255.0, gamma) * 255.0 + 0.5

  #add standard movies from folder to list
  stdMvList.extend([cwd + "/stdMovies/" + f for f in listdir(cwd + "/stdMovies") if isfile(join(cwd + "/stdMovies", f))])

  #start main queue working thread
  worker = Thread(target=_workQueue, args=(movieQueue))
  worker.setDaemon(True)
  worker.start()

def _workQueue(mQueue):
  while True:
    if mQueue.empty():
      mQueue.put(randomMovie())
    mov = mQueue.get()
    _movieEvent(mov)
    movieQueue.task_done()
    _sleepms(50)

def putQueue(movPath):
  global movieQueue
  movieQueue.put(movPath)

def randomMovie():
  global stdMvList
  rN = random.randrange(0,len(stdMvList))
  return stdMvList[rN]

def _movieEvent(mov):
  global numPorts
  framerate = mov.get(cv2.CAP_PROP_FPS)
  while(mov.isOpened()):
    m = mov.read()[1]

    if m is None:
      break
    mwidth, mheight, d = m.shape    

    for i in range(numPorts):
      # copy a portion of the movie's image to the LED image
      xoffset = int(_percentage(mwidth, ledArea[i].x))
      yoffset = int(_percentage(mheight, ledArea[i].y))
      xwidth =  int(_percentage(mwidth, ledArea[i].width))
      yheight = int(_percentage(mheight, ledArea[i].height))
      
      dim = (ledImage[i].shape[0],ledImage[i].shape[1])
      cropImg = m[xoffset:xoffset+xwidth, yoffset:yoffset+yheight]
      ledImage[i] = cv2.resize(cropImg,dim)
      ledData = _image2data(ledImage[i], ledLayout[i])
      
      if (i == 0):
        usec = int((1000000.0 / framerate) * 0.75)
        ledData.insert(0, _npc(usec >> 8))
        ledData.insert(0, _npc(usec))
        ledData.insert(0, ord('*'))
      else:
        ledData[0] = bytes('%','ASCII')  # others sync to the master board
        ledData[1] = 0
        ledData[2] = 0
      
      
      # send the raw data to the LEDs  :-)
      cv2.imshow("x", cropImg)
      time.sleep(framerate/690)
      ledSerial[i].write(ledData)
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
  mov.release()
  


# image2data converts an image to OctoWS2811's raw data format.
# The number of vertical pixels in the image must be a multiple
# of 8.  The data array must be the proper size for the image.
def _image2data(image, layout):
  data = list()
  imageheight = image.shape[0]
  imagewidth = image.shape[1]
  offset = 3
  linesPerPin = int(imageheight / 8)
  pixel = [None] * 8

  flatimg = []
  for imgline in image:
    flatimg.extend(imgline)

  for y in range(linesPerPin):
    if layout: p = 0
    else: p = 1
    if (y & 1) == p:
      # even numbered rows are left to right
      xbegin = 0
      xend = imagewidth
      xinc = 1
    else:
      # odd numbered rows are right to left
      xbegin = imagewidth - 1
      xend = -1
      xinc = -1
    
    for x in range(xbegin,xend,xinc):
      for i in range(8):
        
        pixel[i] = flatimg[x + (y + linesPerPin * i) * imagewidth]
        pixel[i] = _colorWiring(pixel[i])

      # convert 8 pixels to 24 bytes
      mask = 0x800000
      while mask != 0:
        b = 0
        for i in range(8):
          if (pixel[i] & mask) != 0:
            b = b | (1 << i)
        offset += 1
        data.append(b)
        mask >>= 1

  return data

def _npc(x): #narrowing primitive conversion
  pnmask = 0xFF
  return x & pnmask

# translate the 24 bit color from RGB to the actual
# order used by the LED wiring.  GRB is the most common.
def _colorWiring(c):
  red = c[0]
  green = c[1]
  blue = c[2]
  red = int(gammatable[red])
  green = int(gammatable[green])
  blue = int(gammatable[blue])
  return (green << 16) | (blue << 8) | (red)


# ask a Teensy board for its LED configuration, and set up the info for it.
def _serialConfigure(portName):
  global numPorts
  global errorCount
  if numPorts >= maxPorts:
    print("too many serial ports, please increase maxPorts")
    errorCount += 1
    return
  try:
    ledSerial[numPorts] = Serial(portName, write_timeout=1)
    if (ledSerial[numPorts] == None): print('NonePointerException!'); errorCount+=1; return
    ledSerial[numPorts].write(bytes('?','ASCII'))
  except Exception as e:
    print("Serial port " + portName + " does not exist or is non-functional: " + str(e))
    errorCount += 1
    return
  
  _sleepms(50)
  line = ledSerial[numPorts].readline().strip().decode()
  if (line == None):
    print("Serial port " + portName + " is not responding.")
    print("Is it really a Teensy running VideoDisplay?")
    errorCount += 1
    return
  
  param = line.split(",")
  if (len(param) != 12):
    print("Error: port " + portName + " did not respond to LED config query")
    errorCount += 1
    return
  
  # only store the info and increase numPorts if Teensy responds properly
  ledImage[numPorts] = np.zeros((int(param[0]), int(param[1]),3), np.uint8)
  ledArea[numPorts] = Rectangle(int(param[5]), int(param[6]), int(param[7]), int(param[8]))
  ledLayout[numPorts] = int(param[5]) == 0
  numPorts += 1

# scale a number by a percentage, from 0 to 100
def _percentage(num, percent):
  mult = _percentageFloat(percent)
  output = num * mult
  return output


# scale a number by the inverse of a percentage, from 0 to 100
def _percentageInverse(num, percent):
  div = _percentageFloat(percent)
  output = num / div
  return output


# convert an integer from 0 to 100 to a float percentage
# from 0.0 to 1.0.  Special cases for 1/3, 1/6, 1/7, etc
# are handled automatically to fix integer rounding.
def _percentageFloat(percent):
  if (percent == 33): return 1.0 / 3.0
  if (percent == 17): return 1.0 / 6.0
  if (percent == 14): return 1.0 / 7.0
  if (percent == 13): return 1.0 / 8.0
  if (percent == 11): return 1.0 / 9.0
  if (percent ==  9): return 1.0 / 11.0
  if (percent ==  8): return 1.0 / 12.0
  return percent / 100.0

def _sleepms(ms):
  time.sleep(ms / 1000)

#run setup (main program)
setupLED()