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

# Linux systems (including Raspberry Pi) require 49-teensy.rules in
# /etc/udev/rules.d/, and gstreamer compatible with Processing's
# video library.

# To configure this program, edit the following sections:
#
#  1: change myMovie to open a video file of your choice    -)
#
#  2: edit the serialConfigure() lines in setup() for your
#     serial device names (Mac, Linux) or COM ports (Windows)
#
#  3: if your LED strips have unusual color configuration,
#     edit colorWiring().  Nearly all strips have GRB wiring,
#     so normally you can leave this as-is.
#
#  4: if playing 50 or 60 Hz progressive video (or faster),
#     edit framerate in movieEvent().

#import processing.video.*
#import processing.serial.*
#import java.awt.Rectangle

import math, time, cv2, numpy as np
from serial import Serial
from cv2 import cv2

port="COM6"

movieFile = 'Video.mp4'

gamma = 1.7

numPorts=0  # the number of serial ports in use
maxPorts=24 # maximum number of serial ports

#ledSerial = new Serial[maxPorts]     # each port's actual Serial port
#ledArea = new Rectangle[maxPorts] # the area of the movie each port gets, in % (0-100)
#ledLayout = new boolean[maxPorts]   # layout of rows, True = even is left->right
#ledImage = new PImage[maxPorts]      # image sent to each port
ledSerial = [None] * maxPorts
ledArea = [None] * maxPorts
ledLayout = [None] * maxPorts
ledImage = [None] * maxPorts
gammatable = [None] * 256
errorCount = 0
framerate = 0

class Rectangle:
  def __init__(self,x,y,width,height):
    self.x = x
    self.y = y
    self.width = width
    self.height = height

#def settings():
#  size(480, 400)  # create the window

def setup():
  global errorCount
  #slist = Serial.list()
  #sleepms(20)
  #print("Serial Ports List:")
  #print(slist)
  serialConfigure(port)  # change these to your port names
  print(f"using port {port}")
  #serialConfigure("/dev/ttyACM1")
  if (errorCount > 0):
    exit()
  for i in range(256):
    gammatable[i] = math.pow(i / 255.0, gamma) * 255.0 + 0.5
  
  myMovie = cv2.VideoCapture(movieFile)
  #myMovie.loop()  # start the movie :-)
  movieEvent(myMovie)


# movieEvent runs for each new frame of movie data

def movieEvent(mov):
  global numPorts
  while(mov.isOpened()):
    m = mov.read()[1]
    print("movieEvent")
    # read the movie's next frame
    #m.read()
    mwidth, mheight, d = m.shape


    #if (framerate == 0) framerate = m.getSourceFrameRate()
    #framerate = 30.0 # TODO, how to read the frame rate???
    framerate = mov.get(cv2.CAP_PROP_FPS)
    print(framerate)

	

    for i in range(numPorts):
      # copy a portion of the movie's image to the LED image
      xoffset = int(percentage(mwidth, ledArea[i].x))
      yoffset = int(percentage(mheight, ledArea[i].y))
      xwidth =  int(percentage(mwidth, ledArea[i].width))
      yheight = int(percentage(mheight, ledArea[i].height))
      
      dim = (ledImage[i].shape[0],ledImage[i].shape[1])
      cropImg = m[xoffset:xoffset+xwidth, yoffset:yoffset+yheight]
      ledImage[i] = cv2.resize(cropImg,dim)
      # convert the LED image to raw data
      #byte[] ledData =  new byte[(ledImage[i].width * ledImage[i].height * 3) + 3]
      #ledData = bytearray((dim[0] * dim[1] * 3) + 3)
      ledData = bytes()
      
      if (i == 0):
        ledData += bytes('*','ASCII')  # first Teensy is the frame sync master
        
        usec = int((1000000.0 / framerate) * 0.75)
        ledData += bytes(usec)   # request the frame sync pulse
        ledData += bytes(usec >> 8) # at 75% of the frame time
        
      else:
        ledData += bytes('%','ASCII')  # others sync to the master board
        ledData += 0
        ledData += 0
      ledData += image2data(ledImage[i], ledData, ledLayout[i])
      # send the raw data to the LEDs  :-)
      ledSerial[i].write(ledData)
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
  mov.release()
  


# image2data converts an image to OctoWS2811's raw data format.
# The number of vertical pixels in the image must be a multiple
# of 8.  The data array must be the proper size for the image.
def image2data(image, data, layout):
  imageheight = image.shape[0]
  imagewidth = image.shape[1]
  offset = 3
  #x, y, xbegin, xend, xinc, mask
  linesPerPin = int(imageheight / 8)
  pixel = [None] * 8

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
        # fetch 8 pixels from the image, 1 for each pin
        flatimg = []
        for imgline in image:
          flatimg.extend(imgline)
        pixel[i] = flatimg[x + (y + linesPerPin * i) * imagewidth]
        pixel[i] = colorWiring(pixel[i])
        print(pixel[i])
        data += pixel[i]
      
      # convert 8 pixels to 24 bytes
      #for (mask = 0x800000 mask != 0 mask >>= 1):
      mask = 0x800000
      while mask != 0:
        b = 0
        for i in range(8):
          if (pixel[i] & mask) != 0:
            b = b | (1 << i)
        
        offset += 1
        data += bytes(b)
        mask >>= 1
  return data
      
    
  


# translate the 24 bit color from RGB to the actual
# order used by the LED wiring.  GRB is the most common.
def colorWiring(c):
  #red = (c & 0xFF0000) >> 16
  red = c[0]
  #green = (c & 0x00FF00) >> 8
  green = c[1]
  #blue = (c & 0x0000FF)
  blue = c[2]
  red = int(gammatable[red])
  green = int(gammatable[green])
  blue = int(gammatable[blue])
  return (green << 16) | (red << 8) | (blue) # GRB - most common wiring
  #return bytearray([green,red,blue])


# ask a Teensy board for its LED configuration, and set up the info for it.
def serialConfigure(portName):
  global numPorts
  global errorCount
  if numPorts >= maxPorts:
    print("too many serial ports, please increase maxPorts")
    errorCount += 1
    return
  try:
    ledSerial[numPorts] = Serial(portName)
    if (ledSerial[numPorts] == None): print('NonePointerException!'); errorCount+=1; return
    ledSerial[numPorts].write(bytes('?','ASCII'))
  except Exception as e:
    print("Serial port " + portName + " does not exist or is non-functional: " + str(e))
    errorCount += 1
    return
  
  sleepms(50)
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
  
  print(param)
  
  # only store the info and increase numPorts if Teensy responds properly
  #ledImage[numPorts] = new PImage(Integer.parseInt(param[0]), Integer.parseInt(param[1]), RGB)
  ledImage[numPorts] = np.zeros((int(param[0]), int(param[1]),3), np.uint8)
  ledArea[numPorts] = Rectangle(int(param[5]), int(param[6]), int(param[7]), int(param[8]))
  ledLayout[numPorts] = int(param[5]) == 0
  numPorts += 1

"""
# draw runs every time the screen is redrawn - show the movie...
def draw():
  global numPorts
  #print("draw")
  # show the original video
  image(myMovie, 0, 80)

  # then try to show what was most recently sent to the LEDs
  # by displaying all the images for each port.
  for i in range(numPorts):
    # compute the intended size of the entire LED array
    xsize = percentageInverse(ledImage[i].width, ledArea[i].width)
    ysize = percentageInverse(ledImage[i].height, ledArea[i].height)
    # computer this image's position within it
    xloc =  percentage(xsize, ledArea[i].x)
    yloc =  percentage(ysize, ledArea[i].y)
    # show what should appear on the LEDs
    image(ledImage[i], 240 - xsize / 2 + xloc, 10 + yloc)

# respond to mouse clicks as pause/play
isPlaying = True
def mousePressed():
  if (isPlaying):
    myMovie.pause()
    isPlaying = False
  else:
    myMovie.play()
    isPlaying = True
"""

# scale a number by a percentage, from 0 to 100
def percentage(num, percent):
  mult = percentageFloat(percent)
  output = num * mult
  return output


# scale a number by the inverse of a percentage, from 0 to 100
def percentageInverse(num, percent):
  div = percentageFloat(percent)
  output = num / div
  return output


# convert an integer from 0 to 100 to a float percentage
# from 0.0 to 1.0.  Special cases for 1/3, 1/6, 1/7, etc
# are handled automatically to fix integer rounding.
def percentageFloat(percent):
  if (percent == 33): return 1.0 / 3.0
  if (percent == 17): return 1.0 / 6.0
  if (percent == 14): return 1.0 / 7.0
  if (percent == 13): return 1.0 / 8.0
  if (percent == 11): return 1.0 / 9.0
  if (percent ==  9): return 1.0 / 11.0
  if (percent ==  8): return 1.0 / 12.0
  return percent / 100.0

def sleepms(ms):
  time.sleep(ms / 1000)


setup()