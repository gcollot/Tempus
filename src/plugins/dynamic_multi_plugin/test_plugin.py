#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
/**
 *   Copyright (C) 2012-2014 IFSTTAR (http://www.ifsttar.fr)
 *   Copyright (C) 2012-2014 Oslandia <infos@oslandia.com>
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

import sys
import os
import re
import unittest

script_path = os.path.abspath(os.path.dirname(sys.argv[0]))
wps_path = os.path.abspath( script_path + '/../../python' )
sys.path.insert(0, wps_path)
from wps_client import *
from tempus_request import *

WPS_HOST = '127.0.0.1'
WPS_PATH = '/wps'


class TestWPS(unittest.TestCase):

    def setUp(self):
        self.client = HttpCgiConnection( WPS_HOST, WPS_PATH )
        self.wps = WPSClient(self.client)

    def test_plugin( self ):

        tempus = TempusRequest( 'http://' + WPS_HOST + WPS_PATH )

        # we are requesting a U-turn, using a private car
        # where a restriction forbids U-turn to cars
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        origin = Point( 355956.316044, 6688240.140580 ),
                        plugin_options = { 'verbose_algo' : False, "verbose" : False, "walk_at_destination": False },
                        steps = [ RequestStep(destination = Point( 355942.525170, 6688324.111680 )) ],
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [3] # car
                        )
        # the resulting sequence should involve more sections
        self.assertEqual( len(tempus.results[0].steps), 5 )

        # we request the same U_turn, but with a bike
        # (allowed)
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'verbose_algo' : False, "verbose" : False, "walk_at_destination": False },
                        origin = Point( 355956.316044, 6688240.140580 ),
                        steps = [ RequestStep(destination = Point( 355942.525170, 6688324.111680 )) ],
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [2] # bike
                        )
        self.assertEqual( len(tempus.results[0].steps), 3 )

        # we request the same U_turn, but walking
        # there is a shortcut in that case
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'verbose_algo' : False, "verbose" : False, "walk_at_destination": False },
                        origin = Point( 355956.316044, 6688240.140580 ),
                        steps = [ RequestStep(destination = Point( 355942.525170, 6688324.111680 )) ],
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1] # pedestrian
                        )
        self.assertEqual( len(tempus.results[0].steps), 2 )

        # request public transports
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'verbose_algo' : False, "verbose" : False, "walk_at_destination": True },
                        origin = Point( 356291.893979, 6687249.036434),
                        departure_constraint = Constraint( date_time = DateTime(2014,6,18,16,06) ),
                        steps = [ RequestStep(destination = Point( 355365.147244, 6689705.650793 )) ],
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 5] # pedestrian and tram
                        )
        self.assertEqual( len(tempus.results[0].steps), 8 )

        # request a shared bike

        # Keep the bike at destination
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'verbose_algo' : False, "verbose" : False, "walk_at_destination": False },
                        origin = Point(355943.384642, 6687666.979354),
                        steps = [ RequestStep(destination = Point( 355410.137514, 6688374.297960 )) ],
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 8] # pedestrian and shared bike
                        )
        n_road2poi = len([ s for s in tempus.results[0].steps if isinstance(s, TransferStep) and s.mode == 1 and s.final_mode == 8 ])
        n_poi2road = len([ s for s in tempus.results[0].steps if isinstance(s, TransferStep) and s.mode == 8 and s.final_mode == 1 ])
        self.assertEqual( n_road2poi, 1 )
        self.assertEqual( n_poi2road, 0 )

        # This time, park the bike before destination
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'verbose_algo' : False, "verbose" : False, "walk_at_destination": True },
                        origin = Point(355943.384642, 6687666.979354),
                        steps = [ RequestStep(destination = Point( 355410.137514, 6688374.297960 )) ],
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 8] # pedestrian and shared bike
                        )
        n_road2poi = len([ s for s in tempus.results[0].steps if isinstance(s, TransferStep) and s.mode == 1 and s.final_mode == 8 ])
        n_poi2road = len([ s for s in tempus.results[0].steps if isinstance(s, TransferStep) and s.mode == 8 and s.final_mode == 1 ])
        self.assertEqual( n_road2poi, 1 )
        self.assertEqual( n_poi2road, 1 )

if __name__ == '__main__':
    unittest.main()

