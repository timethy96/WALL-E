from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from starlette.requests import Request

import concurrent.futures, os, math, time, aiofiles, sys, json


cwd = os.path.dirname(os.path.realpath(__file__))

sys.path.append(cwd)

import queueWorker

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = [
    "https://wall-e.de",
    "localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class data(BaseModel):
    aqi: Optional[int] = None
    img: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
@limiter.exempt
def read_root():
    return r"For api description please consult the <a href='/docs'>docs</a>"


@app.post("/")
@limiter.limit("30/minute")
async def upload_post(in_file: UploadFile=File(...), length: str=Form(...), recurring: str=Form(...), time: str=Form(...), request: Request=Request):
    if os.path.isfile(cwd + "/qMovies/" + in_file.filename):
        fName = in_file.filename.split(".")[0:-1]
        fExt = in_file.filename.split(".")[-1]
        out_file_path = cwd + "/qMovies/" + fName + str(time.time_ns()) + fExt
    else:
        out_file_path = cwd + "/qMovies/" + in_file.filenames
    async with aiofiles.open(out_file_path, 'wb') as out_file:
        while content := await in_file.read(1024):
            await out_file.write(content)  # async write chunk

    if time:
        if recurring == "1":
            queueWorker.putDB(out_file_path, time, length, recurring)
        else:
            queueWorker.putDB(out_file_path, time, length, 0)
    else:
        queueWorker.putQueue(out_file_path)

    return {"Result": "OK, queued!"}

@app.get("/queue/")
@limiter.limit("30/minute")
async def get_queue():
    return json.dumps(queueWorker.getQueueInfo())


