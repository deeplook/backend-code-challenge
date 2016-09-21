#!/usr/bin/env python

"""
Some very simple functions for database handling.
"""

import os
import sys
import sqlite3
import configparser

import pandas as pd


config_path = 'config.ini'
config = configparser.ConfigParser()
config.read(config_path)
path = config.get('SERVICE', 'database')


def create():
    if os.path.exists(path):
        os.remove(path)

    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cmd = '''CREATE TABLE traffic (
                uid text, 
                type text, 
                timestamp real, 
                longitude real, 
                lattitude real, 
                heading real
            )'''
    cursor.execute(cmd)
    conn.commit()

    os.chmod(path, 0o666)


def dump_sql():
    conn = sqlite3.connect(path)
    for line in conn.iterdump():
        print(line)


def dump_csv():
    conn = sqlite3.connect(path)
    cmd = 'SELECT * FROM traffic'
    df = pd.read_sql_query(cmd, conn)
    print(df.to_csv())


def delete():
    os.remove(path)


def show_usage():
    prog = os.path.basename(sys.argv[0])
    print('Usage: %s create | dump_sql | dump_csv | delete' % prog)
    sys.exit(0)


if __name__ == '__main__':
    try:
        arg = sys.argv[1]
    except IndexError:
        show_usage()
    if arg == 'create':
        create()
    elif arg == 'dump_sql':
        dump_sql()
    elif arg == 'dump_csv':
        dump_csv()
    elif arg == 'delete':
        delete()
    else:
        show_usage()
