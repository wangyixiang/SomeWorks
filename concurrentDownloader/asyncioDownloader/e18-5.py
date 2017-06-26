# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import os
import time

STAR_PHOTO_DIR = "./photos"
STAR_PHOTO_LIST_DIR = "./photolist"


def save_photo(img, star_id, filename):
    path = os.path.join(STAR_PHOTO_DIR, star_id, filename)
    with open(path, "wb") as f:
        f.write(img)


@asyncio.coroutine
def get_photo(url):
    with aiohttp.Timeout(10):
        resp = yield from aiohttp.request("GET", url, headers={" User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"})
        image = yield from resp.read()
    return image


@asyncio.coroutine
def download_one(star_id, url):
    filename = url.split("/")[-1]
    if not os.path.exists(os.path.join(STAR_PHOTO_DIR, star_id, filename)) or \
            (not os.path.getsize(os.path.join(STAR_PHOTO_DIR, star_id, filename)) > 1e3):
        image = yield from get_photo(url)
        save_photo(image, star_id, filename)
    return url

def download_all_for_star(star_id):
    urls = []
    with open(os.path.join(STAR_PHOTO_LIST_DIR, star_id),'r') as f:
        for line in f:
            if len(line.strip()) > 0:
                urls.append(line.strip())
    if len(urls) > 0:
        loop = asyncio.get_event_loop()
        if not os.path.exists(os.path.join(STAR_PHOTO_DIR, star_id)):
            os.mkdir(os.path.join(STAR_PHOTO_DIR, star_id))
        to_download = [download_one(star_id, url) for url in sorted(urls)]
        wait_coro = asyncio.wait(to_download)
        res, _ = loop.run_until_complete(wait_coro)
        loop.close()
    else:
        print("{} don't have any photo in its photo list file.\n".format(star_id))

    return star_id


def main(downloader):
    t0 = time.time()
    star_id = "99"
    count = downloader(star_id)
    elapsed = time.time() - t0
    print("\n{} photo for star {} downloaded in {:.2f}s".format(count, star_id, elapsed))


if __name__ == '__main__':
    main(download_all_for_star)