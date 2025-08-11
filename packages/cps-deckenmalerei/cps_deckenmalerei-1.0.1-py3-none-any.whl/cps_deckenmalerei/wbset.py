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
import hashlib
import logging

from wikibaseintegrator.wbi_config import config as wbi_config

from dotenv import load_dotenv

from cps_deckenmalerei.record import Record
from cps_deckenmalerei.sqlite import Sqlite
from cps_deckenmalerei.entity import Entity

from cps_wb.wikibase import WB
from cps_wb.wikilabel import WikiLabel

from wikibaseintegrator.datatypes import Item, String, URL
from wikibaseintegrator.models import Qualifiers, References, Reference

from translate import Translator

# akamaitechnologies hangs unless it recognises the User-Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134."

# Handles
db = None # SQLITE DB
dbfile = None # SQLITE DB basename
wb = None # WikiBase

# Properties
P = {}

# Lists
ItemList = []   # List of entities

# Dictionaries
RootDict = {}   # Dict of root containers
InstDict = {}   # Dict of entities by instance
QDict    = {}   # Dict of Q items mapped to SQL records
SDict    = {}   # Dict of SQL records mapped to Q items

def main():
    global db, dbfile, wb, P, RootDict, InstDict

    parser = argparse.ArgumentParser()

    parser.add_argument("key", type=str, help="object id or url")

    args = parser.parse_args()

    load_dotenv(os.getcwd() + os.sep + ".env")

    if os.getenv("LOGGING"):
        logging.basicConfig(level=os.getenv("LOGGING"), format="%(asctime)s %(name)s %(message)s")
    else:
        logging.basicConfig(level="INFO", format="%(asctime)s %(name)s %(message)s")

    if not os.getenv("DB_FILE"):
        raise Exception("DB_FILE is missing")

    if not os.getenv("WB_URL"):
        raise Exception("WB_URL is missing")

    if not os.getenv("WB_USERNAME"):
        raise Exception("WB_USERNAME is missing")

    if not os.getenv("WB_PASSWORD"):
        raise Exception("WB_PASSWORD is missing")

    wbi_config["DEFAULT_LANGUAGE"] = "en"
    wbi_config["WIKIBASE_URL"] = os.getenv("WB_URL")
    wbi_config["MEDIAWIKI_API_URL"] = os.getenv("WB_URL") + "w/api.php"
    wbi_config["USER_AGENT"] = USER_AGENT

    ##################################################################
    # Login to Wikibase
    #
    wb = WB(os.getenv("WB_USERNAME"), os.getenv("WB_PASSWORD"))

    ##################################################################
    # Open database
    #
    db = Sqlite(os.getenv("DB_FILE"))
    dbfile = os.path.basename(os.getenv("DB_FILE"))

    ##################################################################
    # Custom Wikibase properties
    #
    # Ensemble/Building
    P["Addr"] = wb.property([WikiLabel("Address", "Address String", "en"),
        WikiLabel("Adresse", "Adresse Zeichenkette", "de")], "string")

    # Photograph
    P["Foto"] = wb.property([WikiLabel("Photograph", "Photograph URL", "en"),
        WikiLabel("Foto", "Foto URL", "de")], "url")

    # DECKENMALEREI DOC
    P["Docs"] = wb.property([WikiLabel("Documentation", "Documentation URL", "en"),
        WikiLabel("Dokumentation", "Dokumentation URL", "de")], "url")
    
    # DECKENMALEREI SOURCE
    P["Src"] = wb.property([WikiLabel("Source", "Source URL", "en"),
        WikiLabel("Ursprung", "Ursprung URL", "de")], "url")

    # DATABASE
    P["DB"] = wb.property([WikiLabel("DB", "Database", "en")], "string")
    P["ID"] = wb.property([WikiLabel("ID", "Entity ID", "en")], "string")

    # Photographer
    P["AUTHOR"] = wb.property([WikiLabel("Author", "Name String", "en"),
        WikiLabel("Urheber", "Name Zeichenkette", "de")], "string")

    # Date
    P["DATE"] = wb.property([WikiLabel("Date", "Date String", "en"),
        WikiLabel("Datum", "Datum Zeichenkette", "de")], "string")

    # Painter
    P["PAINTER"] = wb.property([WikiLabel("Painter", "Painter String", "en"),
        WikiLabel("Maler", "Maler Zeichenkette", "de")], "string")

    # Material
    P["MATERIAL"] = wb.property([WikiLabel("Material", "Material Type", "en"),
        WikiLabel("Material", "Material Typ", "de")], "wikibase-item")

    # Technology
    P["TECHNOLOGY"] = wb.property([WikiLabel("Technology", "Technology Type", "en"),
        WikiLabel("Technik", "Technik Typ", "de")], "wikibase-item")

    # Icon
    P["ICONOGRAPHY"] = wb.property([WikiLabel("Iconography", "Iconography URL", "en"),
        WikiLabel("Ikonographie", "Ikonographie URL", "de")], "url")

    ##################################################################
    # Initialise dictionaries
    #
    translator = Translator(from_lang="de", to_lang="en")
    values, names = db.get_attrib_values("TYP")
    for value in values:
        de = value[names["de_DE"]]
        labelList = [WikiLabel(de, f"Typ", "de")]
        try:
            en = translator.translate(de).strip()
            labelList.append(WikiLabel(en, f"Type", "en"))
        except:
            pass
        RootDict[de] = wb.item(labelList)
        InstDict[de] = []

    ##################################################################
    # Determine root object
    #
    if args.key.startswith("http"):
        entities, names = db.get_entities_byurl(args.key)
        if not entities:
            raise Exception("Unknown object URL")

        root = Entity(entities[0][names["id"]], args.key, entities[0][names["entity_id"]])
    else:
        entity, names = db.get_entity_byid(args.key)
        if not entity:
            raise Exception("Unknown object ID")

        root = Entity(args.key, entity[names["url"]], entity[names["entity_id"]])

    if root.entity_id:
        raise Exception("Not a root object")

    ##################################################################
    # Generate dictionaries
    #
    recurse(root)

    ##################################################################
    # Iterate dictionaries
    #

    # Add item
    for entity in ItemList:
        NewItem(entity)

    # Add item instances to root items
    for typ in InstDict:
        entity = wb.wbi.item.get(RootDict[typ])
        for item in InstDict[typ]:
            entity.add_claims(Item(prop_nr=wb.PInstances, value=item))
        entity.write()

    # Part Of
    PDict = {}
    for item in QDict:
        key = QDict[item]
        if key:
            parent = SDict[key]
            if parent not in PDict:
                PDict[parent] = [item]
            else:
                PDict[parent].append(item)
            entity = wb.wbi.item.get(item)
            entity.add_claims(Item(prop_nr=wb.PPartOf, value=parent))
            entity.write()

    # Parts
    for item in PDict:
        entity = wb.wbi.item.get(item)
        for part in PDict[item]:
            entity.add_claims(Item(prop_nr=wb.PParts, value=part))
        entity.write()

def recurse(parent):
    ItemList.append(parent)

    attribs, names = db.get_attribs_byentity(parent.id)
    name = None
    for attrib in attribs:
        if attrib[names["de_DE"]] == "TYP":
            typ = attrib[names["value"]]
        elif attrib[names["de_DE"]] == "NAME":
            name = attrib[names["value"]]

    entities, names = db.get_entities_byentity(parent.id)
    for entity in entities:
        recurse(Entity(entity[names["id"]], entity[names["url"]], parent.id))

def NewItem(entity):
    attribs, names = db.get_attribs_byentity(entity.id)
    label = None
    instanceof = None
    for attrib in attribs:
        if attrib[names["de_DE"]] == "NAME":
            label = attrib[names['value']]
        elif attrib[names["de_DE"]] == "TYP":
            instanceof = attrib[names['value']]

    if label and instanceof != "Foto":
        description = f"{dbfile}, {entity.id}"
        #
        # INSTANCE
        #
        references = References()
        reference1 = Reference()
        reference1.add(String(prop_nr=P["DB"], value=str(dbfile)))
        references.add(reference1)
        reference2 = Reference()
        reference2.add(String(prop_nr=P["ID"], value=str(entity.id)))
        references.add(reference2)

        items, names = db.get_attrib_values_byentity("ID", entity.id)
        if items:
            reference3 = Reference()
            reference3.add(URL(prop_nr=P["Src"], value=items[0][names["url"]]))
            references.add(reference3)

        claims = [Item(prop_nr=wb.PInstanceOf, value=RootDict[instanceof], references=references)]
        #
        # DATE (MALFORMED)
        #
        items, names = db.get_likeattrib_values_byentity("DATIERUNG [%]", entity.id)
        if items:
            s = items[0][names["de_DE"]].capitalize()
            claims.append(String(prop_nr=P["DATE"], value=str(s)))
        #
        # ADDRESS
        #
        address = None
        items, names = db.get_attrib_values_byentity("ADRESSE", entity.id)
        if items:
            address = items[0][names["de_DE"]]
        items, names = db.get_attrib_values_byentity("BUNDESLAND", entity.id)
        if items:
            if address:
                address = address + ", " + items[0][names["de_DE"]]
            else:
                address = items[0][names["de_DE"]]
        items, names = db.get_attrib_values_byentity("LAND", entity.id)
        if items:
            if address:
                address = address + ", " + items[0][names["de_DE"]]
            else:
                address = items[0][names["de_DE"]]
        if address:
            claims.append(String(prop_nr=P["Addr"], value=str(address)))
        #
        # DOCUMENTATION
        #
        items, names = db.get_attrib_values_byentity("IST DOKUMENTIERT IN", entity.id)
        for item in items:
            claims.append(URL(prop_nr=P["Docs"], value=item[names["url"]]))
        #
        # PAINTER [PAINTING]
        #
        items, names = db.get_attrib_values_byentity("HAT MALER", entity.id)
        if items:
            s = trimtype(items[0][names["de_DE"]])
            claims.append(String(prop_nr=P["PAINTER"], value=str(s)))
        #
        # MATERIAL [PAINTING]
        #
        items, names = db.get_attrib_values_byentity("MATERIAL", entity.id)
        if items:
            s = splittype(items[0][names["de_DE"]])
            for i in s:
                q = wb.item([WikiLabel(i, "Material Typ", "de")], wait=True)
                claims.append(Item(prop_nr=P["MATERIAL"], value=q))
        #
        # TECHNOLOGY [PAINTING]
        #
        items, names = db.get_attrib_values_byentity("TECHNIK", entity.id)
        if items:
            s = splittype(items[0][names["de_DE"]])
            for i in s:
                q = wb.item([WikiLabel(i, "Technik Typ", "de")], wait=True)
                claims.append(Item(prop_nr=P["TECHNOLOGY"], value=q))
        #
        # PRIMARY ICONONGRAPHY [PAINTING]
        #
        items, names = db.get_attrib_values_byentity("PRIMÄRE IKONOGRAPHIE", entity.id)
        if items:
            url = items[0][names["url"]]
            if url.startswith("https://"):
                claims.append(URL(prop_nr=P["ICONOGRAPHY"], value=url))
        #
        # ICONCLASS [PAINTING]
        #
        items, names = db.get_attrib_values_byentity("ICONCLASS", entity.id)
        if items:
            l = items[0][names["url"]].split()
            for url in l:
                if url.startswith("https://"):
                    claims.append(URL(prop_nr=P["ICONOGRAPHY"], value=url))
        #
        # PHOTOS
        #
        items, names = db.get_entities_byeav("TYP", "Foto", entity.id)
        for item in items:
            references = References()
            reference1 = Reference()
            reference1.add(String(prop_nr=P["DB"], value=str(dbfile)))
            references.add(reference1)
            reference2 = Reference()
            reference2.add(String(prop_nr=P["ID"], value=str(item[names["id"]])))
            references.add(reference2)

            qualifiers = Qualifiers()
            attribs, names2 = db.get_attribs_byentity(item[names["id"]])
            for attrib in attribs:
                if attrib[names2["de_DE"]] == "URHEBER":
                    qualifiers.add(String(prop_nr=P["AUTHOR"], value=str(attrib[names2["value"]])))

            claims.append(URL(prop_nr=P["Foto"], value=item[names["url"]], qualifiers=qualifiers, references=references))

        item = wb.item([WikiLabel(label, description, "de")], claims)
        InstDict[instanceof].append(item)

        # Part maps
        QDict[item] = entity.entity_id  # Qn => Parent SQL ID
        SDict[entity.id] = item         # Entity SQL ID => Qn

def trimtype(s):
    # Remove trailing [...]
    try:
        p = s.rindex('[')
        return s[:p - 1]
    except:
        return s

def splittype(s):
    # Split on ;
    l = s.split(';')
    s = []
    for x in l:
        x = x.strip()
        try:
            # Remove -> ...
            p = x.rindex("->")
            x = x[:p - 1]
        except:
            pass
        try:
            # Remove (...)
            p = x.rindex('(')
            x = x[:p - 1]
        except:
            pass
        if x not in s:
            s.append(x.capitalize())
    return s

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
