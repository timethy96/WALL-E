from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from pydantic import BaseModel

from starlette.requests import Request

import concurrent.futures, os, math, aiofiles, sys, json
import RPi.GPIO as GPIO
from time import time_ns
import time

import zipfile


#create zip-file for backup
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))


cwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(cwd)

## Setup GPIO for Relay ##

relayPinArray = [17, 27, 22, 23, 24, 25]

GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
GPIO.setup(relayPinArray,GPIO.OUT, initial=GPIO.HIGH)

for pin in relayPinArray:
    GPIO.output(pin,GPIO.LOW)
    time.sleep(2)

nextToggle = GPIO.HIGH

import queueWorker

##            ##

# Define FastAPI
app = FastAPI(openapi_url="/api/openapi.json")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Accept origins (from env-var komma-separated)
origins = str(os.environ['BASEURLS']).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    #allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# get root (nomally not shown)
@app.get("/", response_class=HTMLResponse)
@limiter.exempt
def read_root():
    return r"For api description please consult the <a href='docs'>docs</a>"

# upload file routine
@app.post("/upload/")
@limiter.limit("30/minute") # limitied to 30 per minute (avoid spamming)
async def upload_post(in_file: UploadFile=File(...), length: Optional[str]=Form(None), recurring: Optional[str]=Form(None), time: Optional[str]=Form(None), password: Optional[str]=Form(None), request: Request=Request):
    if password == os.environ['password']: # check password
        if os.path.isfile(cwd + "/qMovies/" + in_file.filename): # if filename already exists -> append nanoseconds to filename (ensure no overwrite)
            fName = in_file.filename.split(".")[0:-1]
            fExt = in_file.filename.split(".")[-1]
            #print(cwd, "/qMovies/", fName, str(time_ns()), fExt)
            out_file_path = cwd + "/qMovies/" + fName[0] + str(time_ns()) + fExt
        else:
            out_file_path = cwd + "/qMovies/" + in_file.filename
        async with aiofiles.open(out_file_path, 'wb') as out_file: # receive file & write to disk
            while content := await in_file.read(1024):
                await out_file.write(content)  # async write chunk

        if time: # if show-time is set --> it's an image
            if recurring == "1": # if recurring is set
                queueWorker.putDB(out_file_path, time, length, recurring) # put it into the database with all the information
            else:
                queueWorker.putDB(out_file_path, time, length, 0) # or omit recurrence
        else:
            queueWorker.putQueue(out_file_path, length) # else put directly in current queue

        return {"Result": "OK, queued!"}
    else:
        return {"Result": "error. wrong password."}

# return queue information for display on web-interface
@app.get("/queue/")
@limiter.limit("30/minute")
async def get_queue(request: Request=Request):
    return queueWorker.getQueueInfo()

# delete from queue (button from the webinterface)
@app.post("/delQueue/")
@limiter.limit("30/minute")
async def delQ_post(movName: str=Form(...), password: Optional[str]=Form(None), request: Request=Request):
    if password == os.environ['password']:
        try:
            queueWorker.delDB(movName)
            return {"Result": "OK, deleted!"}
        except:
            return {"Result": "error!"}
    else:
        return {"Result": "error. wrong password."}

#returns zip-File with all uploaded Files and deletes unused ones
@app.post("/backup/")
@limiter.limit("2/minute")
async def get_backup(password: Optional[str]=Form(None), request: Request=Request):
    if password == os.environ['password']:
        backupfile = str(time_ns()) + ".zip"
        file_path = os.path.join(cwd, backupfile)
        zipf = zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED)
        zipdir(cwd + '/qMovies/', zipf)
        queueWorker.cleanFiles() # deletes unused files
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="application/zip", filename="wall-e-backup.zip")
        return {"error" : "File not found!"}
    else:
        return {"Result": "error. wrong password."}



@app.post("/power/")
@limiter.limit("2/minute")
async def powerToggle(password: Optional[str]=Form(None), request: Request=Request):
    global relayPinArray, nextToggle
    if password == os.environ['password']:
        if nextToggle == GPIO.HIGH:
            queueWorker.stopWorker()
        for pin in relayPinArray:
            GPIO.output(pin,nextToggle)
            time.sleep(2)
        if nextToggle == GPIO.HIGH:
            nextToggle = GPIO.LOW
            return {"success":"Power OFF"}
        elif nextToggle == GPIO.LOW:
            queueWorker.startWorker()
            nextToggle = GPIO.HIGH
            return {"success":"Power ON"}
        else:
            nextToggle = GPIO.HIGH
            queueWorker.stopWorker()
            for pin in relayPinArray:
                GPIO.output(pin,nextToggle)
                time.sleep(2)
            nextToggle = GPIO.LOW
            return {"error":"powered down"}
    else:
        return {"Result": "error. wrong password."}
    