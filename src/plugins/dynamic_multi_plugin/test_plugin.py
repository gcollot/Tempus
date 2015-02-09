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


class Test(unittest.TestCase):

    def setUp(self):
        self.client = HttpCgiConnection( WPS_HOST, WPS_PATH )
        self.wps = WPSClient(self.client)

    def test_forbidden_movements( self ):

        tempus = TempusRequest( 'http://' + WPS_HOST + WPS_PATH )

        # we are requesting a U-turn, using a private car
        # where a restriction forbids U-turn to cars
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        origin = Point( 355956.316044, 6688240.140580 ),
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False },
                        steps = [ RequestStep(destination = Point( 355942.525170, 6688324.111680 ), private_vehicule_at_destination = True) ],
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [3] # car
                        )
        # the resulting sequence should involve more sections
        self.assertEqual( len(tempus.results[0].steps), 3 )

    def test_modes( self ):

        tempus = TempusRequest( 'http://' + WPS_HOST + WPS_PATH )

        # request public transports
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False },
                        origin = Point( 356171.238242, 6687756.369824 ),
                        steps = [ RequestStep(destination = Point( 355559.445002, 6689088.179658 ),
                                              constraint = Constraint( date_time = DateTime(2014,6,18,16,06), type = 2 )) ], # after
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 5] # pedestrian and TRAM only
                        )
        self.assertEqual(isinstance(tempus.results[0].steps[4], PublicTransportStep), True )
        self.assertEqual(tempus.results[0].steps[4].mode, 5) # TRAM
        self.assertEqual( len(tempus.results[0].steps), 9 )

        # 3 minutes later, should be the same result
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False },
                        origin = Point( 356171.238242, 6687756.369824 ),
                        steps = [ RequestStep(destination = Point( 355559.445002, 6689088.179658 ),
                                              constraint = Constraint( date_time = DateTime(2014,6,18,16,9), type = 2 )) ], # after
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 5] # pedestrian and TRAM only
                        )
        self.assertEqual(isinstance(tempus.results[0].steps[4], PublicTransportStep), True )
        self.assertEqual(tempus.results[0].steps[4].mode, 5) # TRAM
        self.assertEqual( len(tempus.results[0].steps), 9 )

        # request public transports
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False },
                        origin = Point( 356171.238242, 6687756.369824 ),
                        steps = [ RequestStep(destination = Point( 355559.445002, 6689088.179658 ),
                                              constraint = Constraint( date_time = DateTime(2014,6,18,16,9), type = 2 )) ], # after
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 6] # pedestrian and BUS only
                        )
        self.assertEqual(isinstance(tempus.results[0].steps[4], PublicTransportStep), True )
        self.assertEqual(tempus.results[0].steps[4].mode, 6) # BUS
        self.assertEqual( len(tempus.results[0].steps), 13 )

        # request public transports with frequency-based scheduling
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False, "Features/timetable_frequency" : 1 },
                        origin = Point( 356171.238242, 6687756.369824 ),
                        steps = [ RequestStep(destination = Point( 355559.445002, 6689088.179658 ),
                                              constraint = Constraint( date_time = DateTime(2014,6,18,16,06), type = 2  )) ], # after
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 5] # pedestrian and TRAM only
                        )
        self.assertEqual(isinstance(tempus.results[0].steps[4], PublicTransportStep), True )
        self.assertEqual(tempus.results[0].steps[4].mode, 5) # TRAM
        self.assertEqual( len(tempus.results[0].steps), 9 )

        # request public transports with frequency-based scheduling
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False, "Features/timetable_frequency" : 1 },
                        origin = Point( 356171.238242, 6687756.369824 ),
                        steps = [ RequestStep(destination = Point( 355559.445002, 6689088.179658 ),
                                              constraint = Constraint( date_time = DateTime(2014,6,18,16,9), type = 2  )) ], # after
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 6] # pedestrian and BUS only
                        )
        self.assertEqual(isinstance(tempus.results[0].steps[4], PublicTransportStep), True )
        self.assertEqual(tempus.results[0].steps[4].mode, 6) # BUS
        self.assertEqual( len(tempus.results[0].steps), 13 )

        # request a shared bike
        # Use a shared bike
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False },
                        origin = Point(355943.384642, 6687666.979354),
                        steps = [ RequestStep(destination = Point( 355410.137514, 6688374.297960 )) ],
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 8] # pedestrian and shared bike
                        )
        n_road2poi = len([ s for s in tempus.results[0].steps if isinstance(s, TransferStep) and s.mode == 1 and s.final_mode == 8 ])
        n_poi2road = len([ s for s in tempus.results[0].steps if isinstance(s, TransferStep) and s.mode == 8 and s.final_mode == 1 ])
        self.assertEqual( n_road2poi, 1 )
        self.assertEqual( n_poi2road, 1 )

    def test_pt_transfer( self ):

        tempus = TempusRequest( 'http://' + WPS_HOST + WPS_PATH )

        # request public transports
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False },
                        origin = Point( 356171.238242, 6687756.369820 ),
                        steps = [ RequestStep(destination = Point( 355467.660265, 6689901.461590 ),
                                              constraint = Constraint( date_time = DateTime(2014,6,18,16,07), type = 2 )) ], # after
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 5] # pedestrian and TRAM only
                        )
        self.assertEqual(isinstance(tempus.results[0].steps[4], PublicTransportStep), True )
        self.assertEqual(isinstance(tempus.results[0].steps[5], PublicTransportStep), True )
        self.assertEqual(tempus.results[0].steps[4].mode, 5) # TRAM
        self.assertEqual(tempus.results[0].steps[4].route[0], '3') # Line 3
        self.assertEqual(tempus.results[0].steps[5].mode, 5) # TRAM
        self.assertEqual(tempus.results[0].steps[5].route[0], '2') # Line 2 (transfer)

    def test_reverse( self ):

        tempus = TempusRequest( 'http://' + WPS_HOST + WPS_PATH )

        # request public transports
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False },
                        origin = Point( 356172.860489, 6687751.207350 ),
                        steps = [ RequestStep(destination = Point( 355396.434795, 6689302.821110 ),
                                              constraint = Constraint( date_time = DateTime(2014,6,16,16,04), type = 2 )) ], # after
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 5] # pedestrian and TRAM only
                        )
        self.assertEqual(isinstance(tempus.results[0].steps[4], PublicTransportStep), True )
        self.assertEqual(tempus.results[0].steps[4].mode, 5) # TRAM
        self.assertEqual(tempus.results[0].steps[4].route[0], '2') # Line 2
        self.assertEqual( len(tempus.results[0].steps), 9 )

        # arrive before
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False },
                        origin = Point( 356172.860489, 6687751.207350 ),
                        steps = [ RequestStep(destination = Point( 355396.434795, 6689302.821110 ),
                                              constraint = Constraint( date_time = DateTime(2014,6,16,16,20), type = 1 )) ], # before
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 5] # pedestrian and TRAM only
                        )
        # should return the same path
        self.assertEqual(isinstance(tempus.results[0].steps[4], PublicTransportStep), True )
        self.assertEqual(tempus.results[0].steps[4].mode, 5) # TRAM
        self.assertEqual(tempus.results[0].steps[4].route[0], '2') # Line 2
        self.assertEqual( len(tempus.results[0].steps), 9 )

        # arrive before with frequency-based trip
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False, "Features/timetable_frequency" : 1 },
                        origin = Point( 356171.238242, 6687756.369824 ),
                        steps = [ RequestStep(destination = Point( 355559.445002, 6689088.179658 ),
                                              constraint = Constraint( date_time = DateTime(2014,6,18,16,20), type = 1 )) ], # before
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 5] # pedestrian and TRAM only
                        )
        self.assertEqual(isinstance(tempus.results[0].steps[4], PublicTransportStep), True )
        self.assertEqual(tempus.results[0].steps[4].mode, 5) # TRAM
        self.assertEqual( len(tempus.results[0].steps), 9 )

        # path with 2 PT involved
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False },
                        origin = Point( 356172.860489, 6687751.207350 ),
                        steps = [ RequestStep(destination = Point( 357137.197048, 6689740.983045 ),
                                              constraint = Constraint( date_time = DateTime(2014,6,16,16,07), type = 2 )) ], # after
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 5] # pedestrian and TRAM only
                        )
        self.assertEqual(isinstance(tempus.results[0].steps[4], PublicTransportStep), True )
        self.assertEqual(tempus.results[0].steps[4].mode, 5) # TRAM
        self.assertEqual(tempus.results[0].steps[4].route[0], '3') # Line 3
        self.assertEqual(isinstance(tempus.results[0].steps[13], PublicTransportStep), True )
        self.assertEqual(tempus.results[0].steps[13].mode, 5) # TRAM
        self.assertEqual(tempus.results[0].steps[13].route[0], '1') # Line 1

        # path with 2 PT involved, reverted
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False },
                        origin = Point( 356172.860489, 6687751.207350 ),
                        steps = [ RequestStep(destination = Point( 357137.197048, 6689740.983045 ),
                                              constraint = Constraint( date_time = DateTime(2014,6,16,16,36), type = 1 )) ], # before
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 5] # pedestrian and TRAM only
                        )
        self.assertEqual(isinstance(tempus.results[0].steps[4], PublicTransportStep), True )
        self.assertEqual(tempus.results[0].steps[4].mode, 5) # TRAM
        self.assertEqual(tempus.results[0].steps[4].route[0], '3') # Line 3
        self.assertEqual(isinstance(tempus.results[0].steps[9], PublicTransportStep), True )
        self.assertEqual(tempus.results[0].steps[9].mode, 5) # TRAM
        self.assertEqual(tempus.results[0].steps[9].route[0], '1') # Line 1

    def test_parking( self ):

        tempus = TempusRequest( 'http://' + WPS_HOST + WPS_PATH )

        # private car
        # only private car, at destination
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False },
                        origin = Point( 355873.900102, 6687910.974614 ),
                        steps = [ RequestStep(destination = Point( 354712.155537, 6688427.796341 ), private_vehicule_at_destination = True) ],
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [3] # private car
                        )
        self.assertEqual(len(tempus.results[0].steps), 7)

        # walking and private car, at destination
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False },
                        origin = Point( 355873.900102, 6687910.974614 ),
                        steps = [ RequestStep(destination = Point( 354712.155537, 6688427.796341 ), private_vehicule_at_destination = True) ],
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 3] # walking, private car
                        )
        s1 = tempus.results[0].steps[0]
        self.assertEqual( isinstance(s1, TransferStep) and s1.mode == 1 and s1.final_mode == 3, True )
        self.assertEqual(len(tempus.results[0].steps), 8)

        # walking and private car, at destination, with a private parking on the path
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False },
                        origin = Point( 355873.900102, 6687910.974614 ),
                        steps = [ RequestStep(destination = Point( 354712.155537, 6688427.796341 ), private_vehicule_at_destination = True) ],
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 3], # walking, private car
                        parking_location = Point(355745.798990, 6688016.989327)
                        )
        # check that the second step is a transfer
        s2 = tempus.results[0].steps[1]
        self.assertEqual( isinstance(s2, TransferStep) and s2.mode == 1 and s2.final_mode == 3, True )
        self.assertEqual(len(tempus.results[0].steps), 9)

        # walking and private car, with a private parking on the path, but must park before reaching destination
        # car_park_search_time is artificially set to 0
        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False, "Time/car_parking_search_time" : 0 },
                        origin = Point( 355873.900102, 6687910.974614 ),
                        steps = [ RequestStep(destination = Point( 354712.155537, 6688427.796341 ), private_vehicule_at_destination = False) ],
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 3], # walking, private car
                        parking_location = Point(355745.798990, 6688016.989327)
                        )
        # check that the second and n-1 step is a transfer
        s2 = tempus.results[0].steps[1]
        sn = tempus.results[0].steps[-4]
        self.assertEqual( isinstance(s2, TransferStep) and s2.mode == 1 and s2.final_mode == 3, True )
        self.assertEqual( isinstance(sn, TransferStep) and sn.mode == 3 and sn.final_mode == 1, True )

    def test_time(self):
        tempus = TempusRequest( 'http://' + WPS_HOST + WPS_PATH )

        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False },
                        origin = Point( 353512.189791, 6688532.281363 ),
                        steps = [ RequestStep(destination = Point( 360870.494259, 6694129.762149 ),
                                              constraint = Constraint( date_time = DateTime(2014,6,18,16,06), type = 2 ), # after
                                              private_vehicule_at_destination = False) ],
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 5, 6] # walking, bus, tram
        )
        duration1 = tempus.results[0].costs[Cost.Duration]

        tempus.request( plugin_name = 'dynamic_multi_plugin',
                        plugin_options = { 'Debug/verbose_algo' : False, "Debug/verbose" : False },
                        origin = Point( 353512.189791, 6688532.281363 ),
                        steps = [ RequestStep(destination = Point( 360870.494259, 6694129.762149 ),
                                              constraint = Constraint( date_time = DateTime(2014,6,18,16,06), type = 2 ), # after
                                              private_vehicule_at_destination = False) ],
                        criteria = [Cost.Duration],
                        allowed_transport_modes = [1, 5, 6, 8] # walking, shared bike, bus, tram
        )
        duration2 = tempus.results[0].costs[Cost.Duration]
        # duration2 should not be greater than duration1
        self.assertTrue( duration1 >= duration2, "Adding a mode gives a worse result !" )


if __name__ == '__main__':
    unittest.main()


