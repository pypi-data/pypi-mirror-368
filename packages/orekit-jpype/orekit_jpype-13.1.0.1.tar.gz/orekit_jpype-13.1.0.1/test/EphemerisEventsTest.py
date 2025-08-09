"""
original copyright:

/* Copyright 2002-2024 CS GROUP
 * Licensed to CS GROUP (CS) under one or more
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

 Python version translated from Java by Petrus Hyvönen and copilot, 2024

"""
import unittest
import jpype
from jpype import JImplements, JOverride

from orekit_jpype import initVM
initVM()

from orekit_jpype.pyhelpers import setup_orekit_curdir
setup_orekit_curdir("resources")


from org.orekit.propagation.analytical import EcksteinHechlerPropagator, Ephemeris
from org.hipparchus.ode.events import Action
from org.hipparchus.util import FastMath
from org.orekit.bodies import CelestialBodyFactory, OneAxisEllipsoid
from org.orekit.errors import OrekitException
from org.orekit.frames import Frame, FramesFactory
from org.orekit.orbits import KeplerianOrbit, Orbit, OrbitType, PositionAngleType
from org.orekit.propagation import BoundedPropagator, Propagator, SpacecraftState, SpacecraftStateInterpolator
from org.orekit.propagation.events import EclipseDetector, EventDetector
from org.orekit.propagation.events.handlers import EventHandler
from org.orekit.time import AbsoluteDate, DateComponents, TimeComponents, TimeInterpolator, TimeScalesFactory
from org.orekit.utils import IERSConventions
from java.util import ArrayList


@JImplements(EventHandler)
class myContinueOnEvent(object):
        def __init__(self, outer_instance, orb_type) -> None:
            self.outer_instance = outer_instance
            self.orb_type = orb_type

        @JOverride
        def init(self, initialstate, target, detector):
            pass

        @JOverride
        def eventOccurred(self, s, detector, increasing):
            self.outer_instance.assertEqual(self.orb_type, s.getOrbit().getType())
            if increasing:
                self.outer_instance.inEclipsecounter += 1
            else:
                self.outer_instance.outEclipsecounter += 1
            return Action.CONTINUE

        @JOverride
        def resetState(self, detector, oldState):
            return oldState

        @JOverride
        def finish(self, finalState, detector):
            pass

class EphemerisEventsTest(unittest.TestCase):

    inEclipsecounter = 0
    outEclipsecounter = 0

    def testEphemKeplerian(self):
        self.checkEphem(OrbitType.KEPLERIAN)

    def testEphemCircular(self):
        self.checkEphem(OrbitType.CIRCULAR)

    def testEphemEquinoctial(self):
        self.checkEphem(OrbitType.EQUINOCTIAL)

    def testEphemCartesian(self):
        self.checkEphem(OrbitType.CARTESIAN)

    def buildEphem(self, orb_type: OrbitType) -> Ephemeris:
        mass = 2500
        a = 7187990.1979844316
        e = 0.5e-4
        i = 1.7105407051081795
        omega = 1.9674147913622104
        OMEGA = FastMath.toRadians(261)
        lv = 0
        mu  = 3.9860047e14
        ae  = 6.378137e6
        c20 = -1.08263e-3
        c30 = 2.54e-6
        c40 = 1.62e-6
        c50 = 2.3e-7
        c60 = -5.5e-7

        deltaT: float = self.finalDate.durationFrom(self.initDate)

        frame = FramesFactory.getEME2000()

        transPar = KeplerianOrbit(a, e, i, omega, OMEGA, lv, PositionAngleType.TRUE, frame, self.initDate, mu)

        nbIntervals = 720
        propagator = EcksteinHechlerPropagator(transPar, mass, ae, mu, c20, c30, c40, c50, c60)

        tab = []
        for j in range(nbIntervals + 1):
            state = propagator.propagate(self.initDate.shiftedBy((j * deltaT) / nbIntervals))
            tab.append(SpacecraftState(orb_type.convertType(state.getOrbit()),
                                       state.getAttitude(),
                                       state.getMass()))

        interpolator = SpacecraftStateInterpolator(2, frame, frame)

        return Ephemeris(ArrayList(tab), interpolator)


    def buildEclipseDetector(self, org_type: OrbitType) -> EclipseDetector:
        sunRadius = 696000000.
        earthRadius = 6400000.

        ecl = EclipseDetector(CelestialBodyFactory.getSun(), sunRadius,
                              OneAxisEllipsoid(earthRadius, 0.0, FramesFactory.getITRF(IERSConventions.IERS_2010, True))) \
              .withMaxCheck(60.0) \
              .withThreshold(1.0e-3) \
              .withHandler(myContinueOnEvent(self, org_type))

        return ecl

    def checkEphem(self, orb_type):
        self.initDate = AbsoluteDate(DateComponents(2004, 1, 1), TimeComponents.H00, TimeScalesFactory.getUTC())
        self.finalDate = AbsoluteDate(DateComponents(2004, 1, 2), TimeComponents.H00, TimeScalesFactory.getUTC())

        ephem: Ephemeris = self.buildEphem(orb_type)

        ephem.addEventDetector(self.buildEclipseDetector(orb_type))

        computeEnd = AbsoluteDate(self.finalDate, -1000.0)

        ephem.clearStepHandlers()
        state: SpacecraftState = ephem.propagate(computeEnd)
        self.assertEqual(computeEnd, state.getDate())
        self.assertEqual(14, self.inEclipsecounter)
        self.assertEqual(14, self.outEclipsecounter)

    def setUp(self):
        self.inEclipsecounter = 0
        self.outEclipsecounter = 0

