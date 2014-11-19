#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
/**
 *   Copyright (C) 2012-2013 IFSTTAR (http://www.ifsttar.fr)
 *   Copyright (C) 2012-2013 Oslandia <infos@oslandia.com>
 *
 *   This library is free software; you can redistribute it and/or
 *   modify it under the terms of the GNU Library General Public
 *   License as published by the Free Software Foundation; either
 *   version 2 of the License, or (at your option) any later version.
 *   
 *   This library is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *   Library General Public License for more details.
 *   You should have received a copy of the GNU Library General Public
 *   License along with this library; if not, see <http://www.gnu.org/licenses/>.
 */
"""

#
# Tempus data loader

import os

from tools import ShpLoader
from dbtools import PsqlLoader
from importer import ShpImporter

# Module to load OpenStreetMap road data (OSM as shapefile)
class OSMImporter(ShpImporter):
    """This class enables to load OpenStreetMap Shape data into a PostGIS database."""
    # Shapefile names to load, without the extension and prefix. It will be the table name.
    SHAPEFILES = ['highway'] 
    OPT_SHAPEFILES = ['restriction']
    # SQL files to execute before loading shapefiles
    PRELOADSQL = ["reset_import_schema.sql"]
    # SQL files to execute after loading shapefiles 
    POSTLOADSQL = ["osm.sql", "osm_processing.sql"]



