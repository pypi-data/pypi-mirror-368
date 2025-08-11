--
-- Copyright (C) 2025 The Authors
-- All rights reserved.
--
-- This file is part of cps_deckenmalerei.
--
-- cps_deckenmalerei is free software: you can redistribute it and/or
-- modify it under the terms of the GNU General Public License as published
-- by the Free Software Foundation.
--
-- cps_deckenmalerei is distributed in the hope that it will be
-- useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
-- Public License for more details.
--
-- You should have received a copy of the GNU General Public License along
-- with cps_deckenmalerei. If not, see http://www.gnu.org/licenses/
--

------------------------------------------------
--
-- SQL schema for cps_deckenmalerei scrape.
--
-- This uses the EAV model.
-- https://en.wikipedia.org/wiki/Entity%E2%80%93attribute%E2%80%93value_model
--
-- The EAV model has been chosen for the entity attributes because they are
-- either unknown before scraping or it's unknown if they are valuable after
-- scraping.
--
-- NB en_GB translations may not be implemented.
--
------------------------------------------------

-- entity

-- id:		entity's identity
-- url:		entity's URL
-- entity_id:	entity's parent identity

CREATE TABLE entity (
'id'		INTEGER PRIMARY KEY,
'url'		TEXT NOT NULL,
'entity_id'	INTEGER DEFAULT NULL REFERENCES id
);
CREATE UNIQUE INDEX entity_index ON entity(url, entity_id);

------------------------------------------------

-- attribute

CREATE TABLE attrib (
'id'		INTEGER PRIMARY KEY,
'de_DE'		TEXT NOT NULL,
'en_GB'		TEXT DEFAULT NULL
);
CREATE UNIQUE INDEX attrib_de_DE_index ON attrib(de_DE);
CREATE INDEX attrib_en_GB_index ON attrib(en_GB);

-- Eg.
-- INSERT INTO attrib ('id', 'de_DE', 'en_GB') VALUES (1, 'TYP', 'TYPE');

-- All attributes are discovered.

------------------------------------------------

-- entity - attribute - Record value
--
-- entity = Subject, attrib = Predicate, value = Record

CREATE TABLE eav_record (
'id'		INTEGER PRIMARY KEY,
'entity_id'	INTEGER NOT NULL,
'attrib_id'	INTEGER NOT NULL,
'de_DE'		TEXT NOT NULL,
'en_GB'		TEXT DEFAULT NULL,
'url'		TEXT DEFAULT NULL,
FOREIGN KEY('entity_id') REFERENCES entity('id'),
FOREIGN KEY('attrib_id') REFERENCES attrib('id')
);

-- Eg.
-- entity = Painting entity, attrib = Position, value.text = "Ceiling"
-- entity = Photo entity,    attrib = Author,   value.text = "Name"

------------------------------------------------

-- entity - attribute - Entity value
--
-- entity = Subject, attrib = Predicate, value = Entity

-- CREATE TABLE eav_entity (
-- 'id'		INTEGER PRIMARY KEY,
-- 'entity_id'	INTEGER NOT NULL,
-- 'attrib_id'	INTEGER NOT NULL,
-- 'value_id'	INTEGER NOT NULL,
-- FOREIGN KEY('entity_id') REFERENCES entity('id'),
-- FOREIGN KEY('attrib_id') REFERENCES attrib('id'),
-- FOREIGN KEY('value_id')  REFERENCES entity('id')
-- );

-- Eg.
-- entity = Painting entity, attrib = Painter, value = Person entity
-- entity = Photo entity,    attrib = Author,  value = Person entity

------------------------------------------------
