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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from datetime import datetime
import config

class StepSelector( QFrame ):

    coordinates_changed = pyqtSignal()

    def __init__( self, parent, name = "Origin", coordinates_only = False, dock = None ):
        QFrame.__init__( self )
        self.parent = parent
        self.dock = dock

        self.layout = QVBoxLayout( self )
        self.layout.setMargin( 0 )

        self.label = QLabel()
        self.label.setText( name )

        self.layout.addWidget( self.label )

        self.hlayout = QHBoxLayout()
        self.hlayout.setMargin( 0 )
        self.layout.addLayout( self.hlayout )

        self.coordinates = QLineEdit()
        self.selectBtn = QToolButton()
        self.selectBtn.setIcon( QIcon( config.DATA_DIR + "/mouse_cross.png" ) )

        self.hlayout.addWidget( self.coordinates )
        self.hlayout.addWidget( self.selectBtn )

        self.setLayout( self.layout )
        self.setFrameStyle( QFrame.Box )

        self.pvadCheck = None
        self.constraint_types = [ (0, "No constraint"), (1, "Arrive before"), (2, "Depart after") ]
        self.dateEdit = None
        if coordinates_only:
            return

        if name == "Destination":
            self.plusBtn = QToolButton()
            self.plusBtn.setIcon( QIcon( config.DATA_DIR + "/add.png" ) )
            self.hlayout.addWidget( self.plusBtn )
            QObject.connect( self.plusBtn, SIGNAL("clicked()"), self.onAdd )
        else:
            if name != "Origin":
                self.minusBtn = QToolButton()
                self.minusBtn.setIcon( QIcon( config.DATA_DIR + "/remove.png" ) )
                self.hlayout.addWidget( self.minusBtn )
                QObject.connect( self.minusBtn, SIGNAL("clicked()"), self.onRemove )

        self.coordinates.textChanged.connect( self.on_coordinates_changed )

        if name != 'Origin':
            n = datetime.now()
            self.dateEdit = QDateTimeEdit( QDateTime.currentDateTime(), self )
            self.dateEdit.setCalendarPopup( True )
            self.constraintBox = QComboBox()

            for i,e in enumerate(self.constraint_types):
                self.constraintBox.insertItem( i, e[1] )

            self.constraintBox.currentIndexChanged[int].connect( self.on_update_constraint )
            self.constraintBox.setCurrentIndex(0)
            self.on_update_constraint(0)

            self.hlayout2 = QHBoxLayout()
            self.hlayout2.setMargin( 0 )
            self.hlayout2.addWidget( self.constraintBox )
            self.hlayout2.addWidget( QLabel("Date and time") )
            self.hlayout2.addWidget( self.dateEdit )

            self.layout.addLayout( self.hlayout2 )

            self.pvadCheck = QCheckBox( "Private vehicule at destination" )
            self.pvadCheck.setCheckState( Qt.Checked )
            self.layout.addWidget( self.pvadCheck )

    def on_update_constraint( self, idx ):
        self.dateEdit.setEnabled( idx != 0 )

    def on_coordinates_changed( self, new_text ):
        if self.get_coordinates() != [0,0]:
            self.coordinates_changed.emit()

    def set_canvas( self, canvas ):
        self.canvas = canvas

        self.clickTool = QgsMapToolEmitPoint( self.canvas )
        QObject.connect( self.selectBtn, SIGNAL("clicked()"), self.onSelect )

    def get_coordinates( self ):
        if self.coordinates.text().find(',') == -1:
            return [0,0]
        s = self.coordinates.text().split(',')
        try:
            if len(s) == 2:
                return [ float(s[0]), float(s[1]) ]
        except ValueError:
            return [0,0]
        return [ 0, 0 ]

    def set_coordinates( self, xy ):
        if not xy:
            self.coordinates.setText("-- unavailable --")
            return
        if xy == []:
            xy = [ 0, 0 ]
        self.coordinates.setText( "%f, %f" % ( xy[0], xy[1] ) )

    def get_constraint_type( self ):
        if self.dateEdit is None:
            return 0
        return self.constraint_types[self.constraintBox.currentIndex()][0]

    def set_constraint_type( self, idx ):
        if self.dateEdit is None:
            return
        for i, e in enumerate(self.constraint_types):
            if e[0] == idx:
                self.constraintBox.setCurrentIndex( i )

    def set_depart_after_support( self, enabled ):
        k = (2,"Depart after")
        if enabled:
            if k not in self.constraint_types:
                self.constraint_types.append(k)
        else:
            if k in self.constraint_types:
                self.constraint_types.remove(k)

        if self.dateEdit is not None:
            self.constraintBox.clear()
            for i,e in enumerate(self.constraint_types):
                self.constraintBox.insertItem( i, e[1] )

    def set_arrive_before_support( self, enabled ):
        k = (1,"Arrive before")
        if enabled:
            if k not in self.constraint_types:
                self.constraint_types.append(k)
        else:
            if k in self.constraint_types:
                self.constraint_types.remove(k)

        if self.dateEdit is not None:
            self.constraintBox.clear()
            for i,e in enumerate(self.constraint_types):
                self.constraintBox.insertItem( i, e[1] )

    def get_constraint( self ):
        if self.dateEdit is None:
            return None
        return self.dateEdit.dateTime().toString(Qt.ISODate)

    def set_constraint( self, str ):
        if self.dateEdit is None:
            return
        datetime = QDateTime.fromString( str, Qt.ISODate )
        self.dateEdit.setDateTime( datetime )

    def get_pvad( self ):
        if self.pvadCheck is None:
            return True
        return self.pvadCheck.checkState() == Qt.Checked

    def set_pvad( self, check ):
        if self.pvadCheck is None:
            return
        state = Qt.Checked
        if check == False:
            state = Qt.Unchecked
        self.pvadCheck.setCheckState( state )

    def onAdd( self ):
        # we assume the parent widget is a QLayout
        s = StepSelector( self.parent, "Step", False, self.dock )
        # forward the signal
        s.coordinates_changed.connect( lambda: self.coordinates_changed.emit() )
        s.set_canvas( self.canvas )

        # remove the last one
        lw = self.parent.itemAt( self.parent.count() - 1 ).widget()
        self.parent.removeWidget( lw )
        self.parent.addWidget( s )
        # add back the last one
        self.parent.addWidget( lw )

    def onRemove( self ):
        self.parent.removeWidget( self )
        self.close()

        # update pin points layer
        self.coordinates_changed.emit()

    def onSelect( self ):
        # will reset coordinates if needed
        self.dock.resetCoordinates()
        QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.onCanvasClick)
        self.canvas.setMapTool(self.clickTool)

    def onCanvasClick( self, point, button ):
        geom = QgsGeometry.fromPoint(point)
        p = geom.asPoint()
        self.canvas.unsetMapTool( self.clickTool )
        self.set_coordinates( [p.x(), p.y()] )
        QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.onCanvasClick)
        self.canvas.refresh()

        self.coordinates_changed.emit()

