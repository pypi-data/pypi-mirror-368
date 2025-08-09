# -*- coding: utf-8 -*-

"""

/* Copyright 2014 SSC
 * Licensed to CS Syst��mes d'Information (CS) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * CS licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


 """

import orekit_jpype

orekit_jpype.initVM()
# orekit_jpype.initVM(vmargs='-Xcheck:jni,-verbose:jni,-verbose:class,-XX:+UnlockDiagnosticVMOptions')

from org.orekit.frames import FramesFactory, TopocentricFrame
from org.orekit.bodies import OneAxisEllipsoid, GeodeticPoint
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.orbits import KeplerianOrbit
from org.orekit.utils import Constants
from org.orekit.propagation.analytical import KeplerianPropagator
from org.orekit.utils import PVCoordinates, IERSConventions
from org.orekit.propagation.events.handlers import EventHandler, ContinueOnEvent
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.propagation.events import EventDetector
from org.orekit.propagation.events.intervals import AdaptableInterval
from org.hipparchus.ode.events import Action
from org.orekit.propagation.events import AbstractDetector
from org.orekit.propagation import SpacecraftState

from math import radians
import math
import unittest
import sys

import logging
logging.basicConfig(level=logging.DEBUG)

from orekit_jpype.pyhelpers import setup_orekit_curdir

setup_orekit_curdir("resources")
from jpype import JImplements, JOverride, JFloat, JDouble

@JImplements(EventHandler)
class MyEventCounter():
    def __init__(self):
        self.events = 0

    @JOverride
    def init(self, initialstate, target, detector):
        print(initialstate, target, detector)

    @JOverride
    def eventOccurred(self, s, detector, increasing):
        if increasing:
            self.events +=  1
        return Action.CONTINUE

    @JOverride
    def resetState(self, detector, oldState):
        return oldState

    @JOverride
    def finish(self, finalState, detector):
        pass

mycounter = MyEventCounter()

@JImplements(AdaptableInterval)
class MyAdaptableInterval():
    @JOverride
    def currentInterval(self, s: SpacecraftState, isForward: bool):
        return float(AbstractDetector.DEFAULT_MAX_CHECK)


@JImplements(EventDetector)
class MyElevationDetector():
    passes = 0

    def __init__(self, elevation, topo):
        self.elevation = elevation
        self.topo: TopocentricFrame = topo

    @JOverride
    def init(self, s, T):
        pass

    @JOverride
    def getThreshold(self):
        return float(AbstractDetector.DEFAULT_THRESHOLD)

    @JOverride
    def getMaxCheckInterval(self):
        return MyAdaptableInterval()

    @JOverride
    def getMaxIterationCount(self):
        return AbstractDetector.DEFAULT_MAX_ITER

    @JOverride
    def g(self, s):
        tmp = self.topo.getElevation(s.getPVCoordinates().getPosition(), s.getFrame(), s.getDate()) - self.elevation
        return tmp

    @JOverride
    def resetState(self, oldState):
        return oldState

    def getElevation(self):
        return self.elevation

    def getTopocentricFrame(self):
        return self.topo

    @JOverride
    def getHandler(self):
        return mycounter

    @JOverride
    def finish(self, state):
        pass


class EventDetectorTest(unittest.TestCase):

    def testOwnElevationDetector(self):
        initialDate = AbsoluteDate(2014, 1, 1, 23, 30, 00.000, TimeScalesFactory.getUTC())
        inertialFrame = FramesFactory.getEME2000()  # inertial frame for orbit definition
        position = Vector3D(-6142438.668, 3492467.560, -25767.25680)
        velocity = Vector3D(505.8479685, 942.7809215, 7435.922231)
        pvCoordinates = PVCoordinates(position, velocity)
        initialOrbit = KeplerianOrbit(pvCoordinates,
                                      inertialFrame,
                                      initialDate,
                                      Constants.WGS84_EARTH_MU)

        kepler = KeplerianPropagator(initialOrbit)

        ITRF = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
        earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                                 Constants.WGS84_EARTH_FLATTENING,
                                 ITRF)

        # Station
        longitude = radians(45.0)
        latitude = radians(25.0)
        altitude = 0
        station1 = GeodeticPoint(latitude, longitude, float(altitude))
        sta1Frame = TopocentricFrame(earth, station1, "station 1")

        elevation = math.radians(5.0)

        detector = MyElevationDetector(elevation, sta1Frame)
        kepler.addEventDetector(detector)

        finalState = kepler.propagate(initialDate.shiftedBy(60 * 60 * 24.0 * 15))

        print(detector.passes)
        self.assertEqual(52, mycounter.events)

    def tearDown(self) -> None:
        import time
        time.sleep(2.0)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(EventDetectorTest)
    ret = not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    sys.exit(ret)
