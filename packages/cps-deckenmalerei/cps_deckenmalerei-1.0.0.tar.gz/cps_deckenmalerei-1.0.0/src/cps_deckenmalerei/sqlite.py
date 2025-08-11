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
import sqlite3
import tempfile

from translate import Translator

from cps_deckenmalerei.record import Record
from cps_deckenmalerei.snarf import Snarf

def main():
    ##################################################################
    # CLASS TEST AND DEBUG
    #
    pass

class Sqlite:
    ##################################################################
    # DATABASE HANDLES
    #
    _con = None
    _cur = None

    ##################################################################
    # DE -> EN
    #
    _translator = None

    def __init__(self, dbfile=None):

        self._translator = Translator(from_lang="de", to_lang="en")

        if not dbfile:
            dbfile = tempfile.gettempdir() + os.sep + "cps_deckenmalerei.db"

        if os.path.isfile(dbfile):
            self._connect(dbfile)
        else:
            self._connect(dbfile)
            self._create()

    def __del__(self):
        self._con.close()

    def _connect(self, dbfile):
        ##################################################################
        # CREATE DATABASE HANDLES
        #
        self._con = sqlite3.connect(dbfile)
        self._cur = self._con.cursor()

    def _create(self):
        ##################################################################
        # CREATE DATABASE FROM SCHEMA
        #
        schema = os.path.dirname(__file__) + os.sep + "schema.sql"
        with open(schema, 'r') as f:
            s = ''
            for line in f:
                l = line.strip()
                if not l.startswith('--'):
                    l = l.replace('\t', ' ')
                    while '  ' in l:
                        l = l.replace('  ', ' ')
                    s += l
                    if s.endswith(';'):
                        self._cur.execute(s)
                        s = ''
        self._con.commit()

    def snarf(self, url, entity_id):
        ##################################################################
        # SCRAPE PAGE AND STORE IN DATABASE AS EAV RECORDS
        #
        obj = Snarf(url, wantphotos=True)

        object_id = self.set_entity(url, entity_id)

        # NB Object may not have any properties
        for property in obj.properties:
            for record in obj.properties[property]:
                attrib_id = self.set_attrib(property)
                self.set_eav_record(object_id, attrib_id, record)

        # NB Object may not have any photographs
        for photograph in obj.photographs:
            photo_id = self.set_entity(photograph["TYP"].url, object_id)
            for property in photograph:
                attrib_id = self.set_attrib(property)
                record = photograph[property]
                self.set_eav_record(photo_id, attrib_id, record)

        return obj, object_id

    ##################################################################
    # SQL RECORD FUNCTIONS
    ##################################################################

    def get_entity(self, url, entity_id):
        ##################################################################
        # GET OLD ENTITY IF EXISTS
        #
        if entity_id:
            entity = self._cur.execute("SELECT id FROM entity WHERE url=? AND entity_id=?", (url, entity_id)).fetchone()
        else:
            entity = self._cur.execute("SELECT id FROM entity WHERE url=? AND entity_id IS NULL", (url,)).fetchone()
        return entity

    def set_entity(self, url, entity_id):
        ##################################################################
        # SET NEW ENTITY IF DOESN'T EXIST
        #
        entity = self.get_entity(url, entity_id)
        if entity:
            return entity[0]

        self._cur.execute("INSERT INTO entity (url, entity_id) VALUES (?, ?)", (url, entity_id))
        self._con.commit()

        entity = self._cur.execute("SELECT last_insert_rowid()").fetchone()
        return entity[0]

    def get_attrib(self, de):
        ##################################################################
        # GET OLD ATTRIBUTE IF EXISTS
        #
        return self._cur.execute("SELECT id FROM attrib WHERE de_DE=?", (de,)).fetchone()

    def set_attrib(self, de):
        ##################################################################
        # SET NEW ATTRIBUTE IF DOESN'T EXIST
        #
        attrib = self.get_attrib(de)
        if attrib:
            return attrib[0]

        de = de.upper()
        try:
            en = self._translator.translate(de).upper().strip()
        except:
            en = None
        if en:
            self._cur.execute("INSERT INTO attrib (de_DE, en_GB) VALUES (?, ?)", (de, en))
        else:
            self._cur.execute("INSERT INTO attrib (de_DE) VALUES (?)", (de,))

        self._con.commit()

        attrib = self._cur.execute("SELECT last_insert_rowid()").fetchone()
        return attrib[0]

    def get_eav_record(self, entity_id, attrib_id, value):
        ##################################################################
        # GET OLD RECORD IF EXISTS
        #
        return self._cur.execute("SELECT id FROM eav_record WHERE entity_id=? AND attrib_id=? AND de_DE=? AND url=?", (entity_id, attrib_id, value.text, value.url)).fetchone()

    def set_eav_record(self, entity_id, attrib_id, value):
        ##################################################################
        # SET NEW RECORD IF DOESN'T EXIST
        #
        record = self.get_eav_record(entity_id, attrib_id, value)
        if record:
            return record[0]

        self._cur.execute("INSERT INTO eav_record (entity_id, attrib_id, de_DE, url) VALUES (?, ?, ?, ?)", (entity_id, attrib_id, value.text, value.url))
        self._con.commit()

        record = self._cur.execute("SELECT last_insert_rowid()").fetchone()
        return record[0]

    ##################################################################
    # SQL UTILITY FUNCTIONS
    ##################################################################

    def get_attribs(self):
        ##################################################################
        # GET DICTIONARIES OF ALL ATTRIBUTES
        #
        index = dict(self._cur.execute("SELECT id,de_DE FROM attrib ORDER BY id ASC").fetchall())
        value = dict(self._cur.execute("SELECT de_DE,id FROM attrib ORDER BY de_DE ASC").fetchall())
        return index, value

    def get_records_byattrib(self, attrib_id):
        ##################################################################
        # GET RECORDS BY ATTRIBUTE ID
        #
        res = self._cur.execute("SELECT id,entity_id,de_DE,url FROM eav_record WHERE attrib_id=? ORDER BY id ASC", (attrib_id,)).fetchall()
        names = dict(map(reversed, enumerate(list(map(lambda x: x[0], self._cur.description)))))
        return res, names

    def get_values_byattrib(self, attrib_id):
        ##################################################################
        # GET VALUES BY ATTRIBUTE ID
        #
        # DEBUG
        #
        res = self._cur.execute("SELECT DISTINCT(de_DE) FROM eav_record WHERE attrib_id=? ORDER BY id ASC", (attrib_id,)).fetchall()
        names = dict(map(reversed, enumerate(list(map(lambda x: x[0], self._cur.description)))))
        return res, names

    def get_records_byvalue(self, attrib_id, de):
        ##################################################################
        # GET RECORDS BY ATTRIBUTE ID AND VALUE
        #
        res = self._cur.execute("SELECT id,entity_id,url FROM eav_record WHERE attrib_id=? AND de_DE=?", (attrib_id,de)).fetchall()
        names = dict(map(reversed, enumerate(list(map(lambda x: x[0], self._cur.description)))))
        return res, names

    def get_records_byentity(self, entity_id):
        ##################################################################
        # GET RECORDS BY ENTITY ID
        #
        res = self._cur.execute("SELECT id,attrib_id,de_DE,url FROM eav_record WHERE entity_id=?", (entity_id,)).fetchall()
        names = dict(map(reversed, enumerate(list(map(lambda x: x[0], self._cur.description)))))
        return res, names

    def get_attrib_byattrib(self, attrib_id):
        ##################################################################
        # GET ATTRIBUTE BY ATTRIBUTE ID
        #
        res = self._cur.execute("SELECT DISTINCT de_DE,en_GB FROM eav_record WHERE attrib_id=? ORDER BY de_DE LIMIT 0,1", (attrib_id,)).fetchall()
        names = dict(map(reversed, enumerate(list(map(lambda x: x[0], self._cur.description)))))
        if res:
            return res[0], names
        return None, None

    def get_attribs_byentity(self, entity_id):
        ##################################################################
        # GET ATTRIBUTES BY ENTITY ID
        #
        res = self._cur.execute("SELECT attrib.de_DE,attrib.en_GB,eav_record.de_DE AS value,eav_record.url FROM attrib,eav_record WHERE eav_record.entity_id=? AND eav_record.attrib_id=attrib.id ORDER by attrib.de_DE ASC;", (entity_id,)).fetchall()
        names = dict(map(reversed, enumerate(list(map(lambda x: x[0], self._cur.description)))))
        return res, names

    def get_attrib_values(self, attrib):
        ##################################################################
        # GET ATTRIBUTE VALUES
        #
        res = self._cur.execute("SELECT DISTINCT de_DE,en_GB FROM eav_record WHERE attrib_id=(SELECT id FROM attrib WHERE attrib.de_DE=?) ORDER BY de_DE ASC;", (attrib,)).fetchall()
        names = dict(map(reversed, enumerate(list(map(lambda x: x[0], self._cur.description)))))
        return res, names

    def get_attrib_values_byentity(self, attrib, entity_id):
        ##################################################################
        # GET ATTRIBUTE VALUES BY ENTITY
        #
        res = self._cur.execute("SELECT de_DE,en_GB,url FROM eav_record WHERE attrib_id=(SELECT id FROM attrib WHERE attrib.de_DE=?) AND entity_id=? ORDER BY de_DE ASC;", (attrib, entity_id)).fetchall()
        names = dict(map(reversed, enumerate(list(map(lambda x: x[0], self._cur.description)))))
        return res, names

    def get_likeattrib_values_byentity(self, attrib, entity_id):
        ##################################################################
        # GET LIKE ATTRIBUTE VALUES BY ENTITY
        #
        res = self._cur.execute("SELECT de_DE,en_GB,url FROM eav_record WHERE attrib_id=(SELECT id FROM attrib WHERE attrib.de_DE LIKE ?) AND entity_id=? ORDER BY de_DE ASC;", (attrib, entity_id)).fetchall()
        names = dict(map(reversed, enumerate(list(map(lambda x: x[0], self._cur.description)))))
        return res, names

    def get_entities_byurl(self, url):
        ##################################################################
        # GET ENTITIES BY URL
        #
        # NB photograph URLs may not be unique
        #
        res = self._cur.execute("SELECT id,entity_id FROM entity WHERE url=?", (url,)).fetchall()
        names = dict(map(reversed, enumerate(list(map(lambda x: x[0], self._cur.description)))))
        return res, names

    def get_entity_byid(self, id):
        ##################################################################
        # GET ENTITY BY ID
        #
        res = self._cur.execute("SELECT url,entity_id FROM entity WHERE id=? LIMIT 0,1", (id,)).fetchall()
        names = dict(map(reversed, enumerate(list(map(lambda x: x[0], self._cur.description)))))
        if res:
            return res[0], names
        return None, None

    def get_entities_byentity(self, entity_id):
        ##################################################################
        # GET ENTITIES BY ENTITY ID
        #
        res = self._cur.execute("SELECT id,url FROM entity WHERE entity_id=?", (entity_id,)).fetchall()
        names = dict(map(reversed, enumerate(list(map(lambda x: x[0], self._cur.description)))))
        return res, names

    def get_entities_byeav(self, attrib, value, entity_id):
        ##################################################################
        # GET ENTITIES BY EAV
        #
        res = self._cur.execute("SELECT entity.id,entity.url,entity.entity_id FROM entity,eav_record WHERE entity.id=eav_record.entity_id AND eav_record.attrib_id=(SELECT id FROM attrib WHERE de_DE=?) AND eav_record.de_DE=? AND entity.entity_id=? ORDER BY entity.id ASC", (attrib, value, entity_id)).fetchall()
        names = dict(map(reversed, enumerate(list(map(lambda x: x[0], self._cur.description)))))
        return res, names

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
