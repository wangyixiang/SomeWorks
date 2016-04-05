#!/usr/bin/env python
# coding:utf-8
"""
  Author:   yixiang.wang
  Purpose:
  Created: 2016/3/10
"""

import logging
import os

import psycopg2

test_data_sources = [
    {
        "data_path": u"",
        "event": u""
    },
]

data_sources = [
    {
        "data_path": u"",
        "event": u""
    },
]


def collect_from_source(conn, sources):
    for source in sources:
        process_source(conn, source["data_path"])


def process_source(conn, source_path):
    """
    source_path is the full and absolute path of the target node.
    """
    if not os.path.exists(source_path):
        logging.warning("source %s do not exists." % source_path)
        return

    fhandler = logging.FileHandler(u"", encoding="utf-8")
    logging.getLogger().addHandler(fhandler)
    process_dir(conn, source_path)
    logging.getLogger().removeHandler(fhandler)


def process_dir(conn, data_path):

    if not os.path.exists(data_path):
        logging.warning("directory %s do not exists." % data_path)
        return

    is_file = not os.path.isdir(data_path)

    if is_file:
        process_file(conn, data_path)
    else:
        item_list = os.listdir(data_path)
        for item in item_list:
            if (item == u".") or (item == u".."):
                continue
            process_dir(conn, os.path.join(data_path, item))


def process_file(conn, data_path):
    absolute_name = os.path.abspath(data_path)
    record = u""
    process_record(conn, record)


def process_record(conn, record):
    user_name = ""
    domain_name = ""
    password = ""
    event_name = ""
    counts = "0"
    insert_record(conn,
                  user_name, domain_name, password,
                  event_name, counts)


sql_insert_statement = u"""INSERT INTO files
(user_name, domain_name, password,
event_name, counts)
VALUES
(%s,%s,%s,
%s,%s)"""


def insert_record(conn,
                  user_name, domain_name, password,
                  event_name, counts):
    try:
        cursor = conn.cursor()

        cursor.execute(sql_insert_statement,
                       [user_name, domain_name, password,
                        event_name, counts])

        logging.info(user_name)
        conn.commit()

    except psycopg2.DatabaseError as e:
        if e.message.find('invalid byte sequence for encoding "UTF8"') != -1:
            conn.rollback()
            logging.error("ErrorOnDecodingAccount: %s" % user_name)

        else:
            logging.error("FailedOnAccountParsing: %s" % user_name)
            logging.exception(e.message)

    finally:
        cursor.close()


def main():
    # replace the real value when put in the production.
    pgconn = psycopg2.connect(database=u"accountdb", host=u"dbserver", user=u"postgres", password=u"postgres")
    collect_from_source(pgconn, data_sources)
    pgconn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger().handlers[0].setLevel(logging.WARNING)
    main()
