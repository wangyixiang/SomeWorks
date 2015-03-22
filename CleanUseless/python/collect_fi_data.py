#!/usr/bin/env python
# coding:utf-8
"""
  Author:   yixiang.wang
  Purpose: 
  Created: 2015/3/19
"""

import logging
import os
import time

import psycopg2

SERVER_NAME = "fileserver"

test_data_sources = [
    {
        "base_dir": r"C:\source",
        "base_unc": r"\\%s\source" % SERVER_NAME
    },
]
data_sources = [
    {
        "base_dir": r"G:\Builds",
        "base_unc": r"\\%s\Builds" % SERVER_NAME
    },
    {
        "base_dir": r"G:\Builds_BA",
        "base_unc": r"\\%s\Builds_BA" % SERVER_NAME
    },
    {
        "base_dir": r"F:\Documentation",
        "base_unc": r"\\%s\Documentation" % SERVER_NAME
    },
    {
        "base_dir": r"F:\Financing",
        "base_unc": r"\\%s\Financing" % SERVER_NAME
    },
    {
        "base_dir": r"F:\HR",
        "base_unc": r"\\%s\HR" % SERVER_NAME
    },
    {
        "base_dir": r"G:\IT",
        "base_unc": r"\\%s\IT" % SERVER_NAME
    },
    {
        "base_dir": r"F:\Legal",
        "base_unc": r"\\%s\Legal" % SERVER_NAME
    },
    {
        "base_dir": r"F:\Public",
        "base_unc": r"\\%s\Public" % SERVER_NAME
    },
    {
        "base_dir": r"F:\RD",
        "base_unc": r"\\%s\RD" % SERVER_NAME
    },
    {
        "base_dir": r"F:\S&M",
        "base_unc": r"\\%s\S&M" % SERVER_NAME
    },
    {
        "base_dir": r"G:\RD\Streams",
        "base_unc": r"\\%s\Streams" % SERVER_NAME
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


sql_insert_statement = """INSERT INTO file_items 
(fi_absolute_name, fi_unc_name, fi_name, 
fi_dir_name, fi_last_modified_time,fi_size, is_file)
VALUES
(%s,%s,%s,
%s,%s,%s,%s)"""

sql_update_statement = """UPDATE file_items SET
(fi_absolute_name, fi_unc_name, fi_name, 
fi_dir_name, fi_last_modified_time,fi_size, is_file)
=
(%s,%s,%s,
%s,%s,%s,%s)
WHERE
fi_unc_name=%s"""


def process_node(conn, source_path, source_dict, is_file, is_insert=True):
    fi_absolute_name = os.path.abspath(source_path)
    fi_unc_name = basename_2_uncname(fi_absolute_name, source_dict)
    if is_file:
        fi_name = os.path.basename(fi_absolute_name)
        fi_dir_name = os.path.dirname(fi_absolute_name)
    else:
        fi_name = ""
        fi_dir_name = fi_absolute_name
    fi_last_modified_time = psycopg2.TimestampFromTicks(os.path.getmtime(fi_absolute_name))
    fi_size = os.path.getsize(fi_absolute_name)

    try:
        cursor = conn.cursor()

        if is_insert:
            cursor.execute(sql_insert_statement,
                           [fi_absolute_name, fi_unc_name, fi_name, fi_dir_name, fi_last_modified_time, fi_size,
                            is_file])
        else:
            cursor.execute(sql_update_statement,
                           [fi_absolute_name, fi_unc_name, fi_name, fi_dir_name, fi_last_modified_time, fi_size,
                            is_file, fi_unc_name])

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
            print e
    finally:
        cursor.close()


def main():
    pgconn = psycopg2.connect(database="fi_db", host="mycentos", user="fi_dba", password="fidba")
    collect_from_source(pgconn, test_data_sources)
    pgconn.close()


if __name__ == "__main__":
    print time.time()
    main()
    print time.time()
    # Inserting 39000 taking 120seconds
    # Updating 39000 taking 225seconds
    # 1 Thread
