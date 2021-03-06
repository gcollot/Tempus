#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Tempus data loader

import argparse
import provider
import sys


def import_tomtom(args, shape_options):
    """Load Tomtom (Multinet) data into a PostGIS database."""
    Importer = {
        '1409': provider.MultinetImporter1409,
        None: provider.MultinetImporter
    }[args.model_version]
    shape_options['I'] = False
    subs = { 'native_srid' : args.native_srid }
    mni = Importer(args.source, args.speed_profile, args.prefix, args.dbstring, args.logfile, shape_options, not args.noclean, subs)
    return mni.load()


def import_pt(args, substitutions):
    """Load Public Transportation (GTFS) data into a PostGIS database."""
    substitutions['native_srid'] = args.native_srid
    gtfsi = provider.GTFSImporter(args.source, args.dbstring, args.logfile, args.encoding, args.copymode, not args.noclean, substitutions)
    return gtfsi.load()


def import_navteq(args, shape_options):
    """Load Navteq (Navstreets) data into a PostGIS database."""
    subs = { 'native_srid' : args.native_srid }
    ntqi = provider.NavstreetsImporter(args.source, args.prefix, args.dbstring, args.logfile, shape_options, not args.noclean, subs)
    return ntqi.load()


def import_route120(args, shape_options):
    """Load IGN (Route120) data into a PostGIS database."""
    subs = { 'native_srid' : args.native_srid }
    igni = provider.IGNRoute120Importer(args.source, args.prefix, args.dbstring, args.logfile, shape_options, not args.noclean, subs)
    return igni.load()


def import_route500(args, shape_options):
    """Load IGN (Route500) data into a PostGIS database."""
    subs = { 'native_srid' : args.native_srid }
    igni = provider.IGNRoute500Importer(args.source, args.prefix, args.dbstring, args.logfile, shape_options, not args.noclean, subs)
    return igni.load()


def import_osm(args, shape_options):
    """Load OpenStreetMap (as shapefile) data into a PostGIS database."""
    subs = { 'native_srid' : args.native_srid }
    osmi = provider.OSMImporter(args.source, args.prefix, args.dbstring, args.logfile, shape_options, not args.noclean, subs)
    return osmi.load()


def import_poi(args, shape_options, poi_type, substitutions):
    """Load a point shapefile into a PostGIS database."""
    substitutions['native_srid'] = args.native_srid
    poii = provider.POIImporter(args.source, args.prefix, args.dbstring, args.logfile, shape_options, not args.noclean, poi_type, substitutions)
    return poii.load()


def reset_db(args):
    subs = {'native_srid' : args.native_srid}
    r = provider.ResetImporter(source='', dbstring=args.dbstring, logfile=args.logfile, options={}, doclean=False, subs=subs)
    return r.load()

def main():
    shape_options = {}
    parser = argparse.ArgumentParser(description='Tempus data loader')
    parser.add_argument(
        '-s', '--source',
        required=True,
        nargs='+',
        help='The source directory/file to load data from')
    parser.add_argument(
        '-sp', '--speed_profile',
        required=False,
        nargs='+',
        help='The source directory/file to load speed profile data from')
    parser.add_argument(
        '-S', '--srid',
        required=False,
        help="Set the SRID for geometries. Defaults to 4326 (lat/lon).")
    parser.add_argument(
        '-N', '--native-srid',
        required=False,
        help="Set the SRID for the tempus db. Defaults to 2154. To be used when creating/reseting the base",
        default=2154)
    parser.add_argument(
        '-R', '--reset',
        required=False,
        help='Reset the database before importing',
        action='store_true', dest='doreset', default=False)
    parser.add_argument(
        '-t', '--type',
        required=True,
        help='The data type (tomtom, navteq, osm, gtfs, poi, route120, route500)')
    parser.add_argument(
        '-m', '--model-version',
        required=False, default=None, dest='model_version',
        help='The data model version (tomtom version)')
    parser.add_argument(
        '-d', '--dbstring',
        required=False,
        help='The database connection string')
    parser.add_argument(
        '-p', '--prefix',
        required=False,
        help='Prefix for shapefile names', default="")
    parser.add_argument(
        '-l', '--logfile',
        required=False,
        help='Log file for loading and SQL output')
    parser.add_argument(
        '-i', '--insert',
        required=False, action='store_false', dest='copymode', default=True,
        help='Use insert for SQL mode (default to COPY)')
    parser.add_argument(
        '-W', '--encoding',
        required=False,
        help="Specify the character encoding of Shape's attribute column.")
    parser.add_argument(
        '-n', '--noclean',
        required=False, action='store_true', default=False,
        help="Do not clean temporary SQL file after loading.")
    parser.add_argument(
        '-y', '--poitype',
        required=False, default=5,
        help="Poi type (1: Car park, 2: shared car, 3: Cycle, 4:Shared cycle, 5:user)")
    parser.add_argument(
        '-v', '--substitution',
        required=False, nargs='+', default='',
        help="List of column name substitution name:value. See poi.sql and gtfs.sql")
    args = parser.parse_args()

    substitutions = {}
    for v in args.substitution:
        [var, value] = v.split(':')
        substitutions[var] = value

    if args.type in {'tomtom', 'navteq', 'poi', 'osm'}:
        if not args.srid:
            sys.stderr.write("SRID needed for %s data type. Assuming EPSG:4326.\n" % args.type)
            shape_options['s'] = 4326
        else:
            shape_options['s'] = args.srid
    if args.type in ['route120', 'route500']:
        shape_options['s'] = 2154

    if args.copymode:
        shape_options['D'] = True
    if args.encoding:
        shape_options['W'] = args.encoding
    else:
        args.encoding = 'UTF8'
    # default shp2pgsql options
    shape_options['I'] = True
    shape_options['g'] = 'geom'
    shape_options['S'] = True

    # first reset if needed
    if args.doreset:
        reset_db(args)
    else:
        # retrieve srid from database
        native_srid = int(provider.dbtools.exec_sql(args.dbstring, "select value from tempus.metadata where key='srid'"))
        print "Got %d as native SRID from the DB" % native_srid
        args.native_srid = native_srid
        
    if args.type is not None and args.source is not None:
        r = None
        if args.type == 'tomtom':
            r = import_tomtom(args, shape_options)
        elif args.type == 'osm':
            args.source = args.source[0]
            r = import_osm(args, shape_options)
        elif args.type == 'navteq':
            r = import_navteq(args, shape_options)
        elif args.type == 'route120':
            r = import_route120(args, shape_options)
        elif args.type == 'route500':
            r = import_route500(args, shape_options)
        elif args.type == 'gtfs':
            args.source = args.source[0]
            r = import_pt(args, substitutions)
        elif args.type == 'poi':
            try:
                poi_type = int(args.poitype)
                if poi_type not in range(1, 6):
                    raise ValueError
            except ValueError:
                print "Wrong poi type. Assuming User type (5). Correct values are in range 1-5."
                poi_type = 5
            r = import_poi(args, shape_options, poi_type, substitutions)

        if not r:
            print "Error during import !"
            sys.exit(1)
    elif not args.doreset:
        sys.stderr.write("Source and type needed !")
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()
