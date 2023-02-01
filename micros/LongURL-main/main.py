from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from urllib.parse import urlparse
import lib.base62 as Base62
import base64
import os
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("KEY")
SPLIT_TEXT = os.getenv("SPLIT_TEXT")
SERVER_PREFIX = os.getenv("SERVER_PREFIX")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def enctry(s):
    encry_str = ""
    for i, j in zip(s, KEY):
        temp = str(ord(i)+ord(j))+SPLIT_TEXT
        encry_str = encry_str + temp
    s = base64.b64encode(encry_str.encode("utf-8"))
    s = Base62.encodebytes(s)
    return s

def dectry(s):
    s = Base62.decodebytes(s)
    p = base64.b64decode(s).decode("utf-8")
    dec_str = ""
    for i, j in zip(p.split(SPLIT_TEXT)[:-1], KEY):
        temp = chr(int(i) - ord(j))
        dec_str = dec_str+temp
    return dec_str

class Create_long_url(BaseModel):
    original_url: str

@app.post("/create")
def shorten_request(data: Create_long_url):
    if urlparse(data.original_url).scheme == "":
        raise HTTPException(
            status_code=400, detail="URL should have a scheme")
    url_key = enctry(data.original_url)
    return {"url": SERVER_PREFIX + url_key}


@app.get("/{url_key}")
def redirect_to_url(url_key):
    original_url = dectry(url_key)
    return RedirectResponse(original_url)
