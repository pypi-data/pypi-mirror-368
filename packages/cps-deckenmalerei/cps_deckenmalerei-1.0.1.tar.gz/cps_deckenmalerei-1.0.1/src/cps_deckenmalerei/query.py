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
from cps_deckenmalerei.entity import Entity

db = None

def main():
    global db

    parser = argparse.ArgumentParser()

    parser.add_argument("key", type=str, help="object id or url")
    parser.add_argument("-r", "--recurse", action="store_true", help="Resurse object tree")

    args = parser.parse_args()

    load_dotenv(os.getcwd() + os.sep + ".env")

    db = Sqlite(os.getenv("DB_FILE"))

    if args.key.startswith("http"):
        entities, names = db.get_entities_byurl(args.key)
        if not entities:
            raise Exception("Unknown object URL")
        for entity in entities:
            id = entity[names["id"]]
            url = args.key
            entity_id = entity[names["entity_id"]]
            printentity(Entity(id, url, entity_id))
            if args.recurse:
                recurse(id)
    else:
        entity, names = db.get_entity_byid(args.key)
        if not entity:
            raise Exception("Unknown object ID")
        id = args.key
        url = entity[names["url"]]
        entity_id = entity[names["entity_id"]]
        printentity(Entity(id, url, entity_id))
        if args.recurse:
            recurse(id)

def printentity(e):
    print(e)
    attribs, names = db.get_attribs_byentity(e.id)
    for attrib in attribs:
        de = attrib[names["de_DE"]]
        en = attrib[names["en_GB"]]
        value = attrib[names["value"]]
        url = attrib[names["url"]]
        if not url:
            url = ''
        print(f"'{de}', '{en}' = '{value}' {url}")
    print()

def recurse(entity_id):
    entities, names = db.get_entities_byentity(entity_id)
    for entity in entities:
        id = entity[names["id"]]
        url = entity[names["url"]]
        printentity(Entity(id, url, entity_id))
        recurse(id)

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
