import queue, random, sqlite3, sys, subprocess
from threading import Thread
from os import listdir, environ, remove, walk
from os.path import isfile, join, dirname, realpath
from time import sleep
from datetime import datetime, time
from cv2 import cv2
from collections import deque

cwd = dirname(realpath(__file__))

sys.path.append(cwd)

movieQueue = deque()

stdMvList = []


# The MovieObj-Class defines one Movie with all its properties
class MovieObj:
  def __init__(self, filePath, dTime=int(datetime.now().timestamp()), imgLength=None, recurrent=0):
    self.filePath = filePath # local file path
    if dTime is None:
      dTime = int(datetime.now().timestamp()) # time the file is to be displayed
    self.dTime = dTime # time the file is to be displayed
    self.imgLength = imgLength # length the image is to be displayed (NoneType for movies)
    self.recurrent = recurrent # if the movie is recurrent (thus written in the database)
  def getDict(self):
    return vars(self) # returns a dictionary with the values of the MovieObj instead of an ObjectType

# function stops the worker after the current movie
def stopWorker():
  global worker, is_running
  is_running = False # ends the while-loop in the worker
  worker.join() # waits for the worker to end (blocking)

# (re)starts the Worker-Thread
def startWorker():
  global worker
  worker = Thread(target=_workQueue, args=([movieQueue,]))
  worker.start()

# main worker function thread
def _workQueue(mQueue):
  global stdMvList, is_running
  is_running = True
  sqlCon = sqlite3.connect(cwd + "/movDB/movDB.db") #connect to sqlite DB-File
  sqlCur = sqlCon.cursor() #and create a cursor

  # -- start worker loop -- #
  while is_running == True:
    # -- get movies from persistent database -- #
    sqlCur.execute('SELECT * FROM movies WHERE dTime <= ? ',(int(datetime.now().timestamp()),)) # get all database entries, where the Time is already passed (eg. Files to be displayed)
    dbMovies = sqlCur.fetchall()
    for movie in dbMovies:
      mQueue.appendleft(MovieObj(movie[0],movie[1],movie[2],movie[3])) # append these files into the queue
    if not mQueue:
      mQueue.append(_randomMovie()) # add a random Movie if the queue is empty
    movObj = mQueue.popleft() # get the first movie in line (the queue)
    timeskip = False
    if movObj.recurrent == 1:
      # -- skip Movie if recurrence was interrupted (eg. the movie had to be played a long time ago, but it wasn't, so please don't play it a x-times in a row, for every day it was skipped)
      deltaTime = 86400
      while datetime.now().timestamp() - deltaTime > movObj.dTime:
        deltaTime += 86400
        timeskip = True
      sqlCur.execute('UPDATE movies SET dTime = ? WHERE filePath = ?',(movObj.dTime + deltaTime, movObj.filePath))
      sqlCon.commit()
      # --

    # -- Start playing movie -- #
    print('playing ' + movObj.filePath)
    if timeskip == False:
      tmpMov = cv2.VideoCapture(movObj.filePath) # fetch framerate of the movie
      framerate = tmpMov.get(cv2.CAP_PROP_FPS) # fetch framerate of the movie
      tmpMov.release()

      args = [cwd + '/movie2serial/application.linux-arm64/movie2serial', str(movObj.filePath), str(framerate), str(environ['ports'])] #construct movie2serial command movie
      if movObj.imgLength:
        args = [cwd + '/movie2serial/application.linux-arm64/movie2serial', str(movObj.filePath), str(framerate), str(environ['ports']), str(movObj.imgLength)] #construct movie2serial command image
      try:
        pJava = subprocess.run(args, check=True) # open movie2serial java
      except:
        sys.exit(1) # restart container on error
      if not pJava.returncode == 0:
        sys.exit(1) # restart container on error
    
    # -- if the video is not to be shown again, delete from database -- #
    if not movObj.filePath in stdMvList and movObj.recurrent == 0: 
      sqlCur.execute('DELETE FROM movies WHERE filePath = ? ',(movObj.filePath,))
      sqlCon.commit()
    # -- #

    sleep(0.05) # sleep so that while-loop doesn't go too fast in case of error
  
  sqlCon.commit()
  sqlCur.close()

# put file directly into queue
def putQueue(movPath, length=None):
  global movieQueue
  movieQueue.append(MovieObj(movPath, imgLength=length)) # create MovieObj and append to queue

# put file into database for later display
def putDB(filePath, dTime, imgLength, recurrent):
  sqlCon = sqlite3.connect(cwd + "/movDB/movDB.db") #connect to sqlite DB-File
  sqlCur = sqlCon.cursor() #and create a cursor
  dTimeTS = int(datetime.strptime(dTime, "%H:%M").timestamp()) + 2208992400 #adding time from 1900 to 1970, somehow strptime starts at 1900 while today() starts at 1970
  dTimeTS += int(datetime.combine(datetime.today(), time.min).timestamp())
  if dTimeTS < int(datetime.now().timestamp()):
    dTimeTS += 86400 #show the next day
  sqlCur.execute(f"INSERT INTO movies VALUES (?,?,?,?)", (filePath,dTimeTS,imgLength,recurrent))
  sqlCon.commit()
  sqlCur.close()

# returns movieobjects in the queue and the future db as json
def getQueueInfo():
  global movieQueue
  sqlCon = sqlite3.connect(cwd + "/movDB/movDB.db") #connect to sqlite DB-File
  sqlCur = sqlCon.cursor() #and create a cursor
  movies = list()
  sqlCur.execute('SELECT * FROM movies')
  dbMovies = sqlCur.fetchall()
  sqlCur.close()
  for movie in dbMovies:
      movies.append(MovieObj(movie[0],movie[1],movie[2],movie[3]).getDict())
  for movie in movieQueue:
      movies.append(movie)
  movies = sorted(movies, key=lambda k: k['dTime'])
  return movies

# deletes entry from db (helper function)
def delDB(filepath):
  sqlCon = sqlite3.connect(cwd + "/movDB/movDB.db") #connect to sqlite DB-File
  sqlCur = sqlCon.cursor() #and create a cursor
  #remove(filepath)
  sqlCur.execute('DELETE FROM movies WHERE filePath = ? ',(filepath,))
  sqlCon.commit()

# deletes all files, that are not in database or queue
def cleanFiles():
  global movieQueue
  allMovsPaths = []
  sqlCur.execute('SELECT * FROM movies')
  dbMovies = sqlCur.fetchall()
  for movie in dbMovies:
    allMovsPaths.append(movie[0])
  for movie in movieQueue:
    allMovsPaths.append(movie.filePath)
  for root, dirs, files in walk(cwd + '/qMovies/'):
    for file in files:
      file_full_path = join(root,file)
      if file_full_path not in allMovsPaths:
        remove(file_full_path)

# get a random Movie from stdMovies dir
def _randomMovie():
  global stdMvList
  rN = random.randrange(0,len(stdMvList))
  return MovieObj(stdMvList[rN])


#add standard movies from folder to list
stdMvList.extend([cwd + "/stdMovies/" + f for f in listdir(cwd + "/stdMovies") if isfile(join(cwd + "/stdMovies", f))])

sqlCon = sqlite3.connect(cwd + "/movDB/movDB.db") #connect to sqlite DB-File
sqlCur = sqlCon.cursor() #and create a cursor

sqlCur.execute(f"CREATE TABLE IF NOT EXISTS movies(filePath TEXT, dTime BIGINT, imgLength SMALLINT, recurrent BOOLEAN)")

sqlCon.commit()
sqlCur.close()

#start main queue working thread
startWorker()