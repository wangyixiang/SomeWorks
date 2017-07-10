# -*- coding: utf-8 -*-

import asyncio
import collections
import os
import time
from enum import Enum

import aiohttp
from aiohttp import web


DEFAULT_CONCUR_REQ = 5
MAX_CONCUR_REQ = 1000

HTTPStatus = Enum("Status", "ok not_found error")
Result = collections.namedtuple("Result", "status data")


class FetchError(Exception):
    def __init__(self, star_id, url):
        self.star_id = star_id
        self.url = url


STAR_PHOTO_DIR = "./photos"
STAR_PHOTO_LIST_DIR = "./photolist"


def save_photo(img, star_id, filename):
    path = os.path.join(STAR_PHOTO_DIR, star_id, filename)
    try:
        with open(path, "wb") as f:
            f.write(img)
    except Exception as exc:
        print(star_id)
        print(exc)


@asyncio.coroutine
def get_photo(star_id, url):
    while True:
        try:
            resp = yield from aiohttp.request('GET', url)
            break
        except asyncio.TimeoutError:
            print("Timeout Error on {} of star {}".format(url, star_id))
            continue
    if resp.status == 200:
        image = yield from resp.read()
        return image
    elif resp.status == 404:
        raise web.HTTPNotFound()
    else:
        raise aiohttp.http_exceptions.HttpProcessingError(code=resp.status, message=resp.reason, header=resp.header)


@asyncio.coroutine
def download_one(star_id, url, semaphore, verbose):
    try:
        with (yield from semaphore):
            filename = url.split("/")[-1]
            downloaded_it = False
            if not os.path.exists(os.path.join(STAR_PHOTO_DIR, star_id, filename)) or \
                    (not os.path.getsize(os.path.join(STAR_PHOTO_DIR, star_id, filename)) > 1e3):
                image = yield from get_photo(star_id, url)
                downloaded_it = True
    except web.HTTPNotFound:
        status = HTTPStatus.not_found
        msg = "not found"
    except Exception as exc:
        raise FetchError(star_id, url) from exc
    else:
        if downloaded_it:
            save_photo(image, star_id, filename)
        status = HTTPStatus.ok
        msg = "OK"

    return Result(status, star_id + '|' + url)


@asyncio.coroutine
def downloader_coro(star_id, verbose, concur_req, counter):
    semaphore = asyncio.Semaphore(concur_req)
    urls = []
    with open(os.path.join(STAR_PHOTO_LIST_DIR, star_id), 'r') as f:
        for line in f:
            if len(line.strip()) > 0:
                urls.append(line.strip())

    if len(urls) > 0:
        if not os.path.exists(os.path.join(STAR_PHOTO_DIR, star_id)):
            os.mkdir(os.path.join(STAR_PHOTO_DIR, star_id))
        to_download = [download_one(star_id, url, semaphore, False) for url in sorted(urls)]
        to_download_iter = asyncio.as_completed(to_download)
        for future in to_download_iter:
            try:
                res = yield from future
            except FetchError as exc:
                star_id = exc.star_id
                url = exc.url
                try:
                    error_msg = exc.__cause__.args[0]
                except IndexError:
                    error_msg = exc.__cause__.__class__.__name__
                status = HTTPStatus.error
            else:
                status = res.status
            counter[status] += 1
    return counter


def download_all_for_stars(concur_req):
    counter = collections.Counter()
    loop = asyncio.get_event_loop()
    star_photo_list = os.listdir(STAR_PHOTO_LIST_DIR)
    for star_id in star_photo_list:
        coro = downloader_coro(star_id, False, concur_req, counter)
        counter = loop.run_until_complete(coro)
    loop.close()

    return counter


def main(downloader):
    t0 = time.time()
    count = downloader(DEFAULT_CONCUR_REQ)
    elapsed = time.time() - t0
    print("\n{} photo for downloaded in {:.2f}s".format(count[HTTPStatus.ok], elapsed))

if __name__ == '__main__':
    # before it goes, I set the DEFAULT_TIMEOUT of aiohttp client to 30 seconds
    aiohttp.DEFAULT_TIMEOUT = 30
    main(download_all_for_stars)
