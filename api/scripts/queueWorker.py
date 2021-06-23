import queue, random, sqlite3, sys
from threading import Thread
from os import listdir, environ, remove
from os.path import isfile, join, dirname, realpath
from time import sleep
from datetime import datetime, time

cwd = dirname(realpath(__file__))

sys.path.append(cwd)

import movie2serial

movieQueue = queue.Queue()

stdMvList = []
 


class MovieObj:
  def __init__(self, filePath, dTime=int(datetime.now().timestamp()), imgLength=None, recurrent=0):
    self.filePath = filePath
    if dTime is None:
      dTime = int(datetime.now().timestamp())
    self.dTime = dTime
    self.imgLength = imgLength
    self.recurrent = recurrent
  def getDict(self):
    return vars(self)

def _workQueue(mQueue):
  global stdMvList
  sqlCon = sqlite3.connect(cwd + "/movDB.db") #connect to sqlite DB-File
  sqlCur = sqlCon.cursor() #and create a cursor
  while True:
    sqlCur.execute('SELECT * FROM movies WHERE dTime <= ? ',(int(datetime.now().timestamp()),))
    dbMovies = sqlCur.fetchall()
    for movie in dbMovies:
      mQueue.put(MovieObj(movie[0],movie[1],movie[2],movie[3])) # HERE INSTEAD OF APPENDING, WE NEED TO INSERT AT FIRST PLACE! (maybe deque?)
    if mQueue.empty():
      mQueue.put(_randomMovie())
    movObj = mQueue.get()
    if movObj.recurrent == 1:
      sqlCur.execute('UPDATE movies SET dTime = ? WHERE filePath = ?',(movObj.dTime + 86400, movObj.filePath))
      sqlCon.commit()
    movie2serial.movieEvent(movObj.filePath)
    if not movObj.filePath in stdMvList and movObj.recurrent == 0:
      remove(movObj.filePath)
      sqlCur.execute('DELETE FROM movies WHERE filePath = ? ',(movObj.filePath,))
      sqlCon.commit()
    movieQueue.task_done()
    sleep(0.05)
  sqlCon.commit()
  sqlCur.close()

def putQueue(movPath):
  global movieQueue
  movieQueue.put(MovieObj(movPath))

def putDB(filePath, dTime, imgLength, recurrent):
  sqlCon = sqlite3.connect(cwd + "/movDB.db") #connect to sqlite DB-File
  sqlCur = sqlCon.cursor() #and create a cursor
  dTimeTS = int(datetime.strptime(dTime, "%H:%M").timestamp()) + 2208992400 #adding time from 1900 to 1970, somehow strptime starts at 1900 while today() starts at 1970
  dTimeTS += int(datetime.combine(datetime.today(), time.min).timestamp())
  if dTimeTS < int(datetime.now().timestamp()):
    dTimeTS += 86400 #show the next day
  sqlCur.execute(f"INSERT INTO movies VALUES (?,?,?,?)", (filePath,dTimeTS,imgLength,recurrent))
  sqlCon.commit()
  sqlCur.close()

def getQueueInfo():
  global movieQueue
  sqlCon = sqlite3.connect(cwd + "/movDB.db") #connect to sqlite DB-File
  sqlCur = sqlCon.cursor() #and create a cursor
  movies = list()
  sqlCur.execute('SELECT * FROM movies WHERE dTime >= ? ',(int(datetime.now().timestamp()),))
  dbMovies = sqlCur.fetchall()
  sqlCur.close()
  for movie in dbMovies:
      movies.append(MovieObj(movie[0],movie[1],movie[2],movie[3]).getDict()) # TODO: Also add movies from current queue
  return movies



def _randomMovie():
  global stdMvList
  rN = random.randrange(0,len(stdMvList))
  return MovieObj(stdMvList[rN])


#add standard movies from folder to list
stdMvList.extend([cwd + "/stdMovies/" + f for f in listdir(cwd + "/stdMovies") if isfile(join(cwd + "/stdMovies", f))])

sqlCon = sqlite3.connect(cwd + "/movDB.db") #connect to sqlite DB-File
sqlCur = sqlCon.cursor() #and create a cursor


try:
  sqlCur.execute(f"CREATE TABLE movies(filePath TEXT, dTime BIGINT, imgLength SMALLINT, recurrent BOOLEAN)")
except:
  print("Table seems to exist! Load data...")

sqlCon.commit()
sqlCur.close()

#start main queue working thread
worker = Thread(target=_workQueue, args=([movieQueue,]))
#worker.setDaemon(True)
worker.start()