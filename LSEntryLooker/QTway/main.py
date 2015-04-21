#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import logging
import Queue
import multiprocessing
import os
import re
import signal
import sys
import time

import lxml.html as h

import crawlerConfig
import getpage

item_number = 0
item_urls = {}
items_per_page = 0


def init():
    global item_number
    global item_urls
    get_item_urls()
    print item_number
    print item_urls


def doit():
    ds_url_dict = get_datastream_urls()
    try:
        ds_url_file = open(crawlerConfig.ds_url_file, 'w')
        json.dump(ds_url_dict, ds_url_file)
    except StandardError:
        logging.exception("failed at saving data stream urls file.")
    finally:
        if ds_url_file:
            ds_url_file.close()


def _first_time_open_site(url):
    global item_number
    global items_per_page

    if not crawlerConfig.debugging:
        queue = multiprocessing.Queue()

        multiprocessing.Process(target=fetch_items_list_worker, args=(url, queue)).start()
        html = queue.get()

        if html is None:
            logging.warning("Getting nothing from entry page.")
            return

        doc_root = h.fromstring(html)

    else:

        doc_root = h.fromstring(crawlerConfig.debug_list_html)

    item_count_text_div = doc_root.find_class(getpage.STCT_RESULTS_SUMMARY)

    if item_count_text_div:

        item_count_text_str = h.tostring(item_count_text_div[0])
        item_count_text_list = re.findall(getpage.STCT_RESULTS_SUMMARY_PATTERN, item_count_text_str)

        if len(item_count_text_list) != 0:
            item_number = int(item_count_text_list[0].strip())
            logging.debug("Find %d items in the target page" % item_number)

    if item_number <= 0:
        return

    item_list_div = doc_root.find_class(getpage.STCT_ITEMS_LIST)
    items = item_list_div[0].find_class(getpage.STCT_ITEM)
    items_per_page = len(items)
    for item in items:

        if item.attrib['class'].strip().lower() != getpage.STCT_ITEM:
            item_number -= 1
            continue
        item_urls[item.attrib[getpage.STCT_ITEM_DATA_URL]] = item.attrib[getpage.STCT_ITEM_DATA_ROLE]


def fetch_items_list_worker(url, done_queue):
    logging.debug("Starting fetching list from:%s" % url)
    pr = getpage.PageRender(url)
    html = pr.get_html_result()
    done_queue.put(html)
    logging.debug("Finishing fetching list from:%s" % url)
    sys.exit(0)


def items_list_parser(html):
    global item_number
    global item_urls

    if html is None:
        logging.warning("Getting nothing from entry page.")
        return

    doc_root = h.fromstring(html)

    item_list_div = doc_root.find_class(getpage.STCT_ITEMS_LIST)
    items = item_list_div[0].find_class(getpage.STCT_ITEM)

    for item in items:

        if item.attrib['class'].strip().lower() != getpage.STCT_ITEM:
            item_number -= 1
            continue
        item_urls[item.attrib[getpage.STCT_ITEM_DATA_URL]] = item.attrib[getpage.STCT_ITEM_DATA_ROLE]


def get_item_urls():
    global item_number
    global item_urls

    logging.debug("Starting getting the channel list")
    _first_time_open_site(getpage.SITE_TV_COUNTRY_THAILAND)

    if item_number == 0:
        logging.warning("Can't find any item in target page.")
        logging.debug("Finishing getting the channel list")
        return

    remain_items_count = item_number - len(item_urls.keys())
    if remain_items_count % items_per_page == 0:
        process_number = remain_items_count / items_per_page
    else:
        process_number = remain_items_count / items_per_page + 1

    getting_list_done_queue = multiprocessing.Queue()
    process_count = process_number
    while process_count > 0:
        multiprocessing.Process(target=fetch_items_list_worker,
                                args=(getpage.SITE_TV_COUNTRY_THAILAND + "?page=%s" % (process_count + 1),
                                      getting_list_done_queue)
                                ).start()
        process_count -= 1

    process_count = process_number

    while process_count > 0:
        html = getting_list_done_queue.get()
        items_list_parser(html)
        logging.debug("The item_urls contains %s url now, and item count is %s" % (len(item_urls), item_number))
        process_count -= 1

    # we just handle the "player-profile" type url, so we clean up the items_urls

    for item_key in item_urls.keys():
        if item_urls[item_key].lower() == getpage.STCT_ITEM_PLAYER_POPUP:
            del item_urls[item_key]
            item_number -= 1
    logging.debug("And %s items is qualified for next step." % item_number)
    logging.debug("Finishing getting the channel list")


def fetch_item_worker(url, doing_queue, done_queue):
    logging.debug("Starting fetching from:%s" % url)
    pid = multiprocessing.current_process().pid
    doing_queue.put((pid, url))
    pr = getpage.PageRender(url)
    html = pr.get_html_result()
    done_queue.put((pid, url, html))
    logging.debug("Finishing fetching from:%s" % url)
    sys.exit(0)


def item_parser(url, html):
    if html is None:
        logging.warning("Getting nothing from item page %s", url)
        return None

    doc_root = h.fromstring(html)

    item_div = doc_root.find_class(getpage.STCT_ITEM_PLAYER_CLASS)
    try:
        item = item_div[0].get_element_by_id(getpage.STCT_ITEM_JW_PLAYER_ID)
    except Exception as e:
        item = None
    if item is None:
        logging.warning("Can't find the target data in the page %s" % url)
        return None
    if "data-stream" in item.attrib.keys():
        return item.attrib["data-stream"]
    else:
        logging.warning("The target data don't include data-stream attributes.")
        return None


def get_datastream_urls():
    global item_number
    global item_urls
    ds_dict = {}

    logging.debug("Starting getting the channel data stream url")
    getting_item_doing_queue = multiprocessing.Queue()
    getting_item_done_queue = multiprocessing.Queue()

    for item_key in item_urls.keys():
        multiprocessing.Process(target=fetch_item_worker,
                                args=(crawlerConfig.site_address + item_key,
                                      getting_item_doing_queue,
                                      getting_item_done_queue)
                                ).start()
    item_count = item_number
    doing_dict = {}
    undone_dict = {}
    while item_count > 0:
        pid, url = getting_item_doing_queue.get()
        doing_dict[pid] = [url, 0]
        item_count -= 1

    timeout_interval = 15
    timeout_limit = 15 * 16
    last_log_time = 0
    while len(doing_dict.keys()) >= 1:
        start_time = time.time()
        try:
            pid, url, html = getting_item_done_queue.get(True, timeout_interval)
            if pid in doing_dict.keys():
                ds_url = item_parser(url, html)
                ds_dict[url] = ds_url
                del doing_dict[pid]
            else:
                logging.warning("process %s for %s has been remove from doing_queue for timeout reason." %
                                (pid, url))
        except Queue.Empty as ex:
            pass
        passed_time = time.time() - start_time
        for key in doing_dict.keys():
            doing_dict[key][1] += passed_time
            if doing_dict[key][1] - last_log_time >= (timeout_interval * 8):
                last_log_time = doing_dict[key][1]
                logging.info("process %s for url %s has passed %s seconds." % (key, doing_dict[key][0], doing_dict[key][1]))
            if doing_dict[key][1] >= timeout_limit:
                logging.warning("process %s for %s has reached timeout limit %ss, remove it from doing_queue." %
                                (key, doing_dict[key][0], timeout_limit))
                undone_dict[key] = doing_dict[key]
                ds_dict[undone_dict[key][0]] = getpage.STCT_ITEM_FETCHING_TIMEOUT
                del doing_dict[key]

    if len(undone_dict.keys()) > 0:
        logging.debug("clean up the unfinished fetching process.")
        for key in undone_dict.keys():
            logging.warning("process %s for %s has running %s seconds without any result, it will be killed." %
                            (key, undone_dict[key][0], undone_dict[key][1]))
            os.kill(key, signal.SIGQUIT)

    logging.debug("Finishing getting the channel data stream url")
    return ds_dict


def main():
    log_format = "%(process)d:%(levelname)s:%(name)s:%(asctime)s:%(message)s:"
    logging.basicConfig(format=log_format)
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Program Starting!")
    init()
    doit()
    logging.debug("Program Finished!")


if __name__ == '__main__':
    main()
