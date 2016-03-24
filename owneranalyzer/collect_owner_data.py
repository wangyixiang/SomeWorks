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
import sys
import time

import psycopg2

SERVER_NAME = u"fileserver"
GETOWNER = u"getowner.exe"
FILESYSTEMENCODING = sys.getfilesystemencoding()

# http://stackoverflow.com/questions/13426156/python-how-to-use-extended-path-length
# https://msdn.microsoft.com/en-us/library/aa365247(VS.85).aspx
# because we will face the un-believable long path name here, we'd better preparing with it.
EXTENDEDLENGTH = u"\\\\?\\"

test_data_sources = [
    {
        "base_dir": u"C:\\source",
        "base_unc": u"\\\\%s\\source" % SERVER_NAME
    },
]
data_sources = [
    {
        "base_dir": ur"D:\Public",
        "base_unc": ur"\\%s\Public" % SERVER_NAME
    },
    {
        "base_dir": ur"D:\RD",
        "base_unc": ur"\\%s\RD" % SERVER_NAME
    }
]

ignored_files_and_dirs = [
    ur"$RECYCLE.BIN",
]


def collect_from_source(conn, sources):
    for source_dict in sources:
        traverse_source(conn, source_dict["base_dir"], source_dict)


def traverse_source(conn, source_path, source_dict):
    """
    source_path is the full and absolute path of the target node.
    """
    if not os.path.exists(EXTENDEDLENGTH + source_path):
        logging.warn("%s do not exists." % source_path)
        return

    is_file = not os.path.isdir(EXTENDEDLENGTH + source_path)
    process_node(conn, source_path, source_dict, is_file)
    if is_file:
        return

    item_list = os.listdir(EXTENDEDLENGTH + source_path)
    for item in item_list:
        if (item == u".") or (item == u".."):
            continue
        traverse_source(conn, os.path.join(source_path, item), source_dict)


def basename_2_uncname(source_path, source_dict):
    return source_path.replace(source_dict["base_dir"], source_dict["base_unc"], 1)


sql_insert_statement = u"""INSERT INTO files
(absolute_name, unc_name, basename,
dir_name, domain_name, owner_name,
last_modified_time, file_size, is_file)
VALUES
(%s,%s,%s,
%s,%s,%s,
%s,%s,%s)"""

sql_update_statement = u"""UPDATE files SET
(absolute_name, unc_name, basename,
dir_name, domain_name, owner_name,
last_modified_time, file_size, is_file)
=
(%s,%s,%s,
%s,%s,%s,
%s,%s,%s)
WHERE
absolute_name=%s"""


def process_node(conn, source_path, source_dict, is_file, is_insert=True):
    absolute_name = os.path.abspath(source_path)
    owner_name = u""
    domain_name = u""

    try:
        output = subprocess.check_output([GETOWNER.encode(FILESYSTEMENCODING), (EXTENDEDLENGTH + absolute_name).encode(FILESYSTEMENCODING)]).strip().split(os.sep)
        domain_name, owner_name = output[0], output[1]
    except subprocess.CalledProcessError as e:
        logging.exception(e.message)
        return
    except Exception as e:
        logging.error("FailedOnFile: %s" % absolute_name)
        logging.exception(e.message)
        return

    unc_name = basename_2_uncname(absolute_name, source_dict)
    if is_file:
        basename = os.path.basename(absolute_name)
        dir_name = os.path.dirname(absolute_name)
    else:
        basename = u""
        dir_name = absolute_name

    # It's hard to image the file in the file system which without modified timestamp, but this kind sick file exist on
    # our windows NTFS system.
    # when it's empty, the os.path.getmtime will return value 46001572830.34235, it will fail functions from datetime
    # module as I tried, it also failed psycopg2's TimestampFromTicks
    #
    # adding protection here, when it happens using the now time instead.

    last_modified_time = psycopg2.TimestampFromTicks(time.time())
    try:
        last_modified_time = psycopg2.TimestampFromTicks(os.path.getmtime(EXTENDEDLENGTH + absolute_name))
    except Exception as e:
        logging.exception(e.message)

    file_size = os.path.getsize(EXTENDEDLENGTH + absolute_name)

    insert_or_update(conn, is_insert,
                     absolute_name, unc_name, basename,
                     dir_name, domain_name, owner_name,
                     last_modified_time, file_size, is_file)


def insert_or_update(conn, is_insert,
                     absolute_name, unc_name, basename,
                     dir_name, domain_name, owner_name,
                     last_modified_time, file_size, is_file):
    try:
        cursor = conn.cursor()

        if is_insert:
            cursor.execute(sql_insert_statement,
                           [absolute_name, unc_name, basename,
                            dir_name, domain_name, owner_name,
                            last_modified_time, file_size, is_file])
        else:
            cursor.execute(sql_update_statement,
                           [absolute_name, unc_name, basename,
                            dir_name, domain_name, owner_name,
                            last_modified_time, file_size, is_file,
                            absolute_name])
        logging.info(absolute_name)
        conn.commit()

    except psycopg2.DatabaseError as e:
        if e.message.find('invalid byte sequence for encoding "UTF8"') != -1:
            conn.rollback()
            logging.error("ErrorOnDecodingFileName: %s" % absolute_name)
            # process_node(conn, source_path.decode("gb18030"), source_dict, is_file)
            # insert_or_update(conn, is_insert,
            #                  absolute_name.decode("gb18030"), unc_name.decode("gb18030"), basename.decode("gb18030"),
            #                  dir_name.decode("gb18030"), domain_name, owner_name,
            #                  last_modified_time, file_size, is_file)

        elif e.message.find('duplicate key value violates unique constraint') != -1:
            conn.rollback()
            # process_node(conn, source_path, source_dict, is_file, False)
            insert_or_update(conn, not is_insert,
                             absolute_name, unc_name, basename,
                             dir_name, domain_name, owner_name,
                             last_modified_time, file_size, is_file)

        else:
            logging.error("FailedOnFile: %s" % absolute_name)
            logging.exception(e.message)

    finally:
       cursor.close()


def main():
    if not os.path.exists(GETOWNER):
        logging.error("%s is not here, I can't do it with it" % GETOWNER)
        return
    # replace the real value when put in the production.
    pgconn = psycopg2.connect(database="filesdb", host="dbserver", user="postgres", password="postgres")
    collect_from_source(pgconn, data_sources)
    pgconn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger().handlers[0].setLevel(logging.WARNING)
    fhandler = logging.FileHandler(u"getowner.log", encoding="utf-8")
    logging.getLogger().addHandler(fhandler)
    main()
