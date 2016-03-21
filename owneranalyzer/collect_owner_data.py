#!/usr/bin/env python
# coding:utf-8
"""
  Author:   yixiang.wang
  Purpose: 
  Created: 2016/3/21
"""

import logging
import os
import subprocess
import time

import psycopg2

SERVER_NAME = "fileserver"
GETOWNER = "getowner.exe"

test_data_sources = [
    {
        "base_dir": r"C:\source",
        "base_unc": r"\\%s\source" % SERVER_NAME
    },
]
data_sources = [
    {
        "base_dir": r"D:\IT",
        "base_unc": r"\\%s\IT" % SERVER_NAME
    },
    {
        "base_dir": r"D:\Public",
        "base_unc": r"\\%s\Public" % SERVER_NAME
    },
    {
        "base_dir": r"D:\RD",
        "base_unc": r"\\%s\RD" % SERVER_NAME
    }
]

ignored_files_and_dirs = [
    "$RECYCLE.BIN",
]


def collect_from_source(conn, sources):
    for source_dict in sources:
        traverse_source(conn, source_dict["base_dir"], source_dict)


def traverse_source(conn, source_path, source_dict):
    """
    source_path is the full and absolute path of the target node.
    """
    if not os.path.exists(source_path):
        logging.warn("%s do not exists.")

    is_file = not os.path.isdir(source_path)
    process_node(conn, source_path, source_dict, is_file)
    if is_file:
        return

    item_list = os.listdir(source_path)
    for item in item_list:
        if (item == ".") or (item == ".."):
            continue
        traverse_source(conn, os.path.join(source_path, item), source_dict)


def basename_2_uncname(source_path, source_dict):
    return source_path.replace(source_dict["base_dir"], source_dict["base_unc"], 1)


sql_insert_statement = """INSERT INTO files
(absolute_name, unc_name, basename,
dirname, ownername, domainname,
last_modified_time, filesize, is_file)
VALUES
(%s,%s,%s,
%s,%s,%s,
%s,%s,%s)"""

sql_update_statement = """UPDATE files SET
(absolute_name, unc_name, basename,
dirname, ownername, domainname,
last_modified_time, filesize, is_file)
=
(%s,%s,%s,
%s,%s,%s,
%s,%s,%s)
WHERE
absolute_name=%s"""


def process_node(conn, source_path, source_dict, is_file, is_insert=True):
    absolute_name = os.path.abspath(source_path)

    unc_name = basename_2_uncname(absolute_name, source_dict)
    if is_file:
        basename = os.path.basename(absolute_name)
        dirname = os.path.dirname(absolute_name)
    else:
        basename = ""
        dirname = absolute_name
    last_modified_time = psycopg2.TimestampFromTicks(os.path.getmtime(absolute_name))
    filesize = os.path.getsize(absolute_name)

    try:
        cursor = conn.cursor()

        if is_insert:
            cursor.execute(sql_insert_statement,
                           [absolute_name, unc_name, basename, dirname, last_modified_time, filesize,
                            is_file])
        else:
            cursor.execute(sql_update_statement,
                           [absolute_name, unc_name, basename, dirname, last_modified_time, filesize,
                            is_file, unc_name])

        conn.commit()
    except psycopg2.DatabaseError as e:
        if e.message.find('invalid byte sequence for encoding "UTF8"') != -1:
            logging.exception(e)
            conn.rollback()
            process_node(conn, source_path.decode("gb18030"), source_dict, is_file)

        elif e.message.find('duplicate key value violates unique constraint') != -1:
            conn.rollback()
            process_node(conn, source_path, source_dict, is_file, False)

        else:
            logging.exception(e.message)
    finally:
        cursor.close()


def main():
    if not os.path.exists(GETOWNER):
        logging.error("%s is not here, I can't do it with it" % GETOWNER)
        return
    pgconn = psycopg2.connect(database="", host="", user="postgre", password="postgre")
    collect_from_source(pgconn, test_data_sources)
    pgconn.close()


if __name__ == "__main__":
    main()

