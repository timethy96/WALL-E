import queue, random, sqlite3, sys
from threading import Thread
from os import listdir, environ, remove
from os.path import isfile, join, dirname, realpath
from time import sleep, time

cwd = dirname(realpath(__file__))

sys.path.append(cwd)

import movie2serial

movieQueue = queue.Queue()

stdMvList = []
 
#add standard movies from folder to list
stdMvList.extend([cwd + "/stdMovies/" + f for f in listdir(cwd + "/stdMovies") if isfile(join(cwd + "/stdMovies", f))])

#start main queue working thread
worker = Thread(target=_workQueue, args=([movieQueue,]))
#worker.setDaemon(True)
worker.start()

sqlCon = sqlite3.connect(cwd + "/movDB.db") #connect to sqlite DB-File
sqlCur = sqlCon.cursor() #and create a cursor
try:
  sqlCur.execute(f"CREATE TABLE movies(filePath TEXT, dTime TIMESTAMP, imgLength SMALLINT, recurrent BOOLEAN)")
except:
  print("Table seems to exist! Load data...")

class MovieObj:
  def __init__(self, filePath, dTime=time(), imgLength=None, recurrent=0):
    self.filePath = filePath
    if dTime is None:
      dTime = time()
    self.dTime = dTime
    self.imgLength = imgLength
    self.recurrent = recurrent
  

def _workQueue(mQueue):
  global stdMvList
  while True:
    sqlCur.execute('SELECT * FROM movies WHERE dTime <= ? ',(time(),))
    dbMovies = sqlCur.fetchall()
    for movie in dbMovies:
      mQueue.put(MovieObj(movie[0],movie[1],movie[2],movie[3])) # HERE INSTEAD OF APPENDING, WE NEED TO INSERT AT FIRST PLACE! (maybe deque?)
    if mQueue.empty():
      mQueue.put(_randomMovie())
    movObj = mQueue.get()
    movie2serial.movieEvent(movObj)
    if not movObj.filePath in stdMvList and movObj.recurrent == 0:
      remove(movObj.filePath)
      sqlCur.execute('DELETE FROM movies WHERE filePath = ? ',(movObj.filePath,))
      sqlCon.commit()
    if movObj.recurrent == 1:
      sqlCur.execute('UPDATE movies SET dTime = ? WHERE filePath = ?',(movObj.dTime + 84600, movObj.filePath))
    movieQueue.task_done()
    sleep(0.05)

def putQueue(movPath):
  global movieQueue
  movieQueue.put(MovieObj(movPath))

def putDB(filePath, dTime, imgLength, recurrent):
  sqlCur.execute(f"INSERT INTO movies VALUES (?,?,?,?)", (filePath,dTime,imgLength,recurrent))
  sqlCon.commit()

def getQueueInfo():
  global movieQueue
  movies = set()
  sqlCur.execute('SELECT * FROM movies WHERE dTime <= ? ',(time(),))
  dbMovies = sqlCur.fetchall()
  for movie in dbMovies:
      movies.add(MovieObj(movie[0],movie[1],movie[2],movie[3]))
  return movies



def _randomMovie():
  global stdMvList
  rN = random.randrange(0,len(stdMvList))
  return MovieObj(stdMvList[rN])