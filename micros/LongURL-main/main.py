# webserver
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# for make long url
from urllib.parse import urlparse
import lib.base62 as Base62
import base64
# env
import os
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("KEY")
SPLIT_TEXT = os.getenv("SPLIT_TEXT")
SERVER_PREFIX = os.getenv("SERVER_PREFIX")
# init webserver
app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "https://localhost",
    "https://localhost:8080",
    "https://localhost:8000",
    "https://jhihyulin.live",
    "https://www.jhihyulin.live",
    "https://l.jhihyulin.live",
    "https://lurl.jhihyulin.live"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加密


def enctry(s):
    encry_str = ""
    for i, j in zip(s, KEY):  # i為字符，j為秘鑰字符
        # 加密字符 = 字符的Unicode碼 + 秘鑰的Unicode碼
        temp = str(ord(i)+ord(j))+SPLIT_TEXT
        encry_str = encry_str + temp
    s = base64.b64encode(encry_str.encode("utf-8"))
    s = Base62.encodebytes(s)
    return s


# 解密
def dectry(s):
    s = Base62.decodebytes(s)
    p = base64.b64decode(s).decode("utf-8")
    dec_str = ""
    for i, j in zip(p.split(SPLIT_TEXT)[:-1], KEY):  # i 為加密字符，j為秘鑰字符
        # 解密字符 = (加密Unicode碼字符 - 秘鑰字符的Unicode碼)的單字節字符
        temp = chr(int(i) - ord(j))
        dec_str = dec_str+temp
    return dec_str


class Create_long_url(BaseModel):
    firebase_uid: str
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
    """
    Check the url_key is in DB, redirect to original url.
    """

    #raise HTTPException(status_code=404, detail="Key not found")
    original_url = dectry(url_key)
    return RedirectResponse(original_url)
