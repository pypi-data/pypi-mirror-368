#! /usr/bin/env python3
#
# Copyright (C) 2025 The Authors
# All rights reserved.
#
# This file is part of cps_deckenmalerei.
#
# cps_deckenmalerei is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation.
#
# cps_deckenmalerei is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with cps_deckenmalerei. If not, see http://www.gnu.org/licenses/
#
import argparse
import os

from dotenv import load_dotenv

from cps_deckenmalerei.sqlite import Sqlite

from time import sleep

db = None

def main():
    global db

    parser = argparse.ArgumentParser()

    parser.add_argument("url", type=str, help="url or file of urls")

    args = parser.parse_args()

    load_dotenv(os.getcwd() + os.sep + ".env")

    db = Sqlite(os.getenv("DB_FILE"))

    if args.url.startswith("https://www.deckenmalerei.eu/"):
        recurse(args.url, None, 0)
    else:
        try:
            f = open(args.url, "r", encoding="utf-8")
        except:
            raise Exception("Invalid url or file of urls")

        for line in f:
            url = line.strip()
            recurse(url, None, 0)

        f.close()

def recurse(url, entity_id, spc):
    obj, entity_id = db.snarf(url, entity_id)

    sleep(5)

    if obj.properties:
        print(spc * ' ' + f"{obj.properties['TYP'][0]}", flush=True)

    for photograph in obj.photographs:
        print(spc * ' ' + f"{photograph['TYP']}", flush=True)

    parts = obj.hat_teil()

    for part in parts:
        recurse(part.url, entity_id, 1 + spc)

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
