from typing import Optional

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from starlette.requests import Request

import concurrent.futures, os, math, time, aiofiles

from movie2serial import putQueue

cwd = os.path.dirname(os.path.realpath(__file__))

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

@app.get("/", response_class=HTMLResponse)
@limiter.exempt
def read_root():
    return r"For api description please consult the <a href='/docs'>docs</a>"


@app.post("/")
@limiter.limit("30/minute")
async def post_endpoint(in_file: UploadFile=File(...), request: Request=Request):
    if os.path.isfile(cwd + "/stdMovies/" + in_file.filename):
        out_file_path = cwd + "/stdMovies/" + in_file.filename + time.time_ns()
    else:
        out_file_path = cwd + "/stdMovies/" + in_file.filename
    async with aiofiles.open(out_file_path, 'wb') as out_file:
        while content := await in_file.read(1024):
            await out_file.write(content)  # async write chunk

    putQueue(out_file_path)

    return {"Result": "OK, queued!"}