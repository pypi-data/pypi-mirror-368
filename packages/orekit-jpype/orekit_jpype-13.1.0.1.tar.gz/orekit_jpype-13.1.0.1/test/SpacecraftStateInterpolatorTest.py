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
import math
import unittest
from jpype import JImplements, JOverride, JByte
import jpype
import numpy as np

from orekit_jpype import initVM

initVM()

from orekit_jpype.pyhelpers import setup_orekit_curdir
setup_orekit_curdir("resources")

# no org.*, java.* imports above!!
# all orekit imports needs to come after the JVM is initialized
from org.orekit.attitudes import BodyCenterPointing
from org.orekit.propagation.analytical import EcksteinHechlerPropagator
from org.hipparchus.geometry.euclidean.threed import Rotation, Vector3D
from org.hipparchus.linear import Array2DRowRealMatrix
from org.hipparchus.util import FastMath
from org.orekit.bodies import CelestialBody, CelestialBodyFactory, OneAxisEllipsoid
from org.orekit.data import DataSource
from org.orekit.errors import OrekitException, OrekitIllegalArgumentException, OrekitMessages
from org.orekit.files.ccsds.definitions import CelestialBodyFrame
from org.orekit.files.ccsds.ndm import ParsedUnitsBehavior, ParserBuilder, WriterBuilder
from org.orekit.files.ccsds.ndm.odm import CartesianCovariance, KeplerianElements, SpacecraftParameters
from org.orekit.files.ccsds.utils.generation import Generator, KvnGenerator
from org.orekit.frames import FactoryManagedFrame, Frame, FramesFactory, LOFType
from org.orekit.orbits import KeplerianOrbit, PositionAngleType
from org.orekit.time import AbsoluteDate, AbstractTimeInterpolator, DateComponents, TimeComponents, TimeScalesFactory
from org.orekit.utils import AbsolutePVCoordinates, AngularDerivativesFilter, CartesianDerivativesFilter, Constants, IERSConventions, PVCoordinates, TimeStampedPVCoordinates
from java.nio.charset import StandardCharsets
from org.orekit.files.ccsds.ndm.odm.opm import OpmWriter
from java.io import ByteArrayInputStream, CharArrayWriter, IOException
from java.net import URISyntaxException
from java.util import ArrayList, HashMap
from java.io import File
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.hipparchus.linear import Array2DRowRealMatrix
from org.hipparchus.util import FastMath
from org.orekit.bodies import CelestialBody, CelestialBodyFactory
from org.orekit.data import DataSource
from org.orekit.errors import OrekitException, OrekitIllegalArgumentException, OrekitMessages
from org.orekit.files.ccsds.definitions import CelestialBodyFrame
from org.orekit.files.ccsds.ndm import ParsedUnitsBehavior, ParserBuilder, WriterBuilder
from org.orekit.files.ccsds.ndm.odm import CartesianCovariance, KeplerianElements, SpacecraftParameters
from org.orekit.files.ccsds.utils.generation import Generator, KvnGenerator
from org.orekit.frames import Frame, FramesFactory, LOFType
from org.orekit.orbits import PositionAngleType
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.utils import Constants, IERSConventions, PVCoordinates, TimeStampedPVCoordinates
from java.nio.charset import StandardCharsets
from org.orekit.files.ccsds.ndm.odm.opm import OpmWriter
from java.io import ByteArrayInputStream, CharArrayWriter, IOException
from java.net import URISyntaxException
from java.util import ArrayList, HashMap
from java.io import File
from org.orekit.propagation import SpacecraftState, SpacecraftStateInterpolator
from org.orekit.forces.gravity import HolmesFeatherstoneAttractionModel, SingleBodyAbsoluteAttraction
from org.orekit.forces.gravity.potential import GravityFieldFactory, NormalizedSphericalHarmonicsProvider
from org.orekit.propagation.numerical import NumericalPropagator
from org.hipparchus.ode.nonstiff import DormandPrince853Integrator

class SpacecraftStateInterpolatorTest(unittest.TestCase):
    def setUp(self):
        try:

            mu = 3.9860047e14
            ae = 6.378137e6
            c20 = -1.08263e-3
            c30 = 2.54e-6
            c40 = 1.62e-6
            c50 = 2.3e-7
            c60 = -5.5e-7

            self.mass = 2500
            a = 7187990.1979844316
            e = 0.5e-4
            i = 1.7105407051081795
            omega = 1.9674147913622104
            OMEGA = FastMath.toRadians(261)
            lv = 0

            date = AbsoluteDate(DateComponents(2004, 1, 1),
                                TimeComponents.H00,
                                TimeScalesFactory.getUTC())
            frame: FactoryManagedFrame = FramesFactory.getEME2000()
            self.orbit = KeplerianOrbit(a, e, i, omega, OMEGA, lv, PositionAngleType.TRUE, frame, date, mu)
            earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                                     Constants.WGS84_EARTH_FLATTENING,
                                     FramesFactory.getITRF(IERSConventions.IERS_2010, True))

            self.absPV = AbsolutePVCoordinates(frame, date, self.orbit.getPVCoordinates())

            self.attitudeLaw = BodyCenterPointing(self.orbit.getFrame(), earth)
            self.orbitPropagator = EcksteinHechlerPropagator(self.orbit, self.attitudeLaw, self.mass,
                                                             ae, mu, c20, c30, c40, c50, c60)

            self.absPVPropagator: NumericalPropagator = self.setUpNumericalPropagator()

        except OrekitException as oe:
            self.fail(oe.getLocalizedMessage())

    def tearDown(self):
        self.mass = None
        self.orbit = None
        self.attitudeLaw = None
        
    def setUpNumericalPropagator(self) -> NumericalPropagator:
        integrator: DormandPrince853Integrator = self.setUpIntegrator()

        propagator = NumericalPropagator(integrator)

        # Configure propagator
        propagator.setOrbitType(None)

        # Add force models
        itrf: FactoryManagedFrame = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
        provider: NormalizedSphericalHarmonicsProvider = GravityFieldFactory.getNormalizedProvider(6, 6)
        potential = HolmesFeatherstoneAttractionModel(itrf, provider)

        propagator.addForceModel(potential)
        propagator.addForceModel(SingleBodyAbsoluteAttraction(CelestialBodyFactory.getEarth()))

        # Set initial state
        initialState = SpacecraftState(self.absPV)

        propagator.setInitialState(initialState)

        # Set attitude law
        propagator.setAttitudeProvider(self.attitudeLaw)

        return propagator


    def setUpIntegrator(self) -> DormandPrince853Integrator:
        dP = 1
        minStep = 0.001
        maxStep = 100
        tolerances = NumericalPropagator.tolerances(dP, self.absPV)

        return DormandPrince853Integrator(minStep, maxStep, tolerances[0], tolerances[1])

    def checkAbsPVInterpolationError(self, n, expectedErrorP, expectedErrorV, expectedErrorA, expectedErrorM, interpolator):
        centerDate: AbsoluteDate = self.absPV.getDate().shiftedBy(100.0)
        sample = []
        for i in range(n):
            dt = i * 900.0 / (n - 1)
            state = self.absPVPropagator.propagate(centerDate.shiftedBy(dt))
            state = state.addAdditionalData("quadratic", dt * dt).addAdditionalStateDerivative("quadratic-dot", dt * dt)
            sample.append(state)

        maxErrorP = 0
        maxErrorV = 0
        maxErrorA = 0
        maxErrorM = 0
        dt = 0
        while dt < 900.0:
            interpolated = interpolator.interpolate(centerDate.shiftedBy(dt), sample)
            propagated = self.absPVPropagator.propagate(centerDate.shiftedBy(dt))
            dpv = PVCoordinates(propagated.getPVCoordinates(), interpolated.getPVCoordinates())
            maxErrorP = max(maxErrorP, dpv.getPosition().getNorm())
            maxErrorV = max(maxErrorV, dpv.getVelocity().getNorm())
            maxErrorA = max(maxErrorA, math.degrees(Rotation.distance(interpolated.getAttitude().getRotation(), propagated.getAttitude().getRotation())))
            maxErrorM = max(maxErrorM, abs(interpolated.getMass() - propagated.getMass()))
            dt += 5

        assert math.isclose(expectedErrorP, maxErrorP, abs_tol=1e-1)
        assert math.isclose(expectedErrorV, maxErrorV, abs_tol=1e-1)
        assert math.isclose(expectedErrorA, maxErrorA, abs_tol=1e-1)
        assert math.isclose(expectedErrorM, maxErrorM, abs_tol=1e-1)



    def checkInterpolationError(self, n, expectedErrorP, expectedErrorV, expectedErrorA, expectedErrorM, expectedErrorQ, expectedErrorD, interpolator):
        centerDate = self.orbit.getDate().shiftedBy(100.0)
        sample = []
        for i in range(n):
            dt = i * 900.0 / (n - 1)
            state = self.orbitPropagator.propagate(centerDate.shiftedBy(dt))
            state = state.addAdditionalData("quadratic", dt * dt).addAdditionalStateDerivative("quadratic-dot", dt * dt)
            sample.append(state)

        maxErrorP = 0
        maxErrorV = 0
        maxErrorA = 0
        maxErrorM = 0
        maxErrorQ = 0
        maxErrorD = 0
        dt = 0
        while dt < 900.0:
            interpolated = interpolator.interpolate(centerDate.shiftedBy(dt), sample)
            propagated = self.orbitPropagator.propagate(centerDate.shiftedBy(dt))
            dpv = PVCoordinates(propagated.getPVCoordinates(), interpolated.getPVCoordinates())
            maxErrorP = max(maxErrorP, dpv.getPosition().getNorm())
            maxErrorV = max(maxErrorV, dpv.getVelocity().getNorm())
            maxErrorA = max(maxErrorA, math.degrees(Rotation.distance(interpolated.getAttitude().getRotation(), propagated.getAttitude().getRotation())))
            maxErrorM = max(maxErrorM, abs(interpolated.getMass() - propagated.getMass()))
            maxErrorQ = max(maxErrorQ, abs(interpolated.getAdditionalState("quadratic")[0] - dt * dt))
            maxErrorD = max(maxErrorD, abs(interpolated.getAdditionalStateDerivative("quadratic-dot")[0] - dt * dt))
            dt += 5

        assert math.isclose(expectedErrorP, maxErrorP, abs_tol=1e-1)
        assert math.isclose(expectedErrorV, maxErrorV, abs_tol=1e-1)
        assert math.isclose(expectedErrorA, maxErrorA, abs_tol=1e-1)
        assert math.isclose(expectedErrorM, maxErrorM, abs_tol=1e-1)
        assert math.isclose(expectedErrorQ, maxErrorQ, abs_tol=1e-1)
        assert math.isclose(expectedErrorD, maxErrorD, abs_tol=1e-1)

    def testOrbitInterpolation(self):
        # Given
        interpolationPoints1 = 2
        interpolationPoints2 = 3
        interpolationPoints3 = 4

        intertialFrame = FramesFactory.getEME2000()

        # When & Then
        # Define state interpolators
        interpolator1 = SpacecraftStateInterpolator(interpolationPoints1, intertialFrame, intertialFrame)

        interpolator2 = SpacecraftStateInterpolator(interpolationPoints2, intertialFrame, intertialFrame)

        interpolator3 = SpacecraftStateInterpolator(interpolationPoints3, intertialFrame, intertialFrame)

        # When & Then
        self.checkInterpolationError(interpolationPoints1, 106.46533, 0.40709287, 169847806.33e-9, 0.0, 450 * 450, 450 * 450,
                                interpolator1)
        self.checkInterpolationError(interpolationPoints3, 0.00002, 0.00000023, 232.25e-9, 0.0, 0.0, 0.0, interpolator3)
        self.checkInterpolationError(interpolationPoints2, 0.00353, 0.00003250, 189886.01e-9, 0.0, 0.0, 0.0, interpolator2)

    def build_all_type_of_interpolator(self, interpolation_points, inertial_frame):
        pva_filters = list(CartesianDerivativesFilter.values())
        angular_filters = list(AngularDerivativesFilter.values())

        dim = len(pva_filters)
        interpolators = []

        for i in range(dim):
            interpolator = SpacecraftStateInterpolator(interpolation_points,
                                                        AbstractTimeInterpolator.DEFAULT_EXTRAPOLATION_THRESHOLD_SEC,
                                                        inertial_frame, inertial_frame,
                                                        pva_filters[i], angular_filters[i])
            interpolators.append(interpolator)

        return interpolators


    def testAbsPVAInterpolation(self):
        # Given
        interpolationPoints1 = 2
        interpolationPoints2 = 3
        interpolationPoints3 = 4

        intertialFrame = self.absPV.getFrame()

        # Create interpolator with different number of interpolation points and derivative filters (P/R, PV/RR, PVA/RRR)
        interpolator1 = self.build_all_type_of_interpolator(interpolationPoints1, intertialFrame)
        interpolator2 = self.build_all_type_of_interpolator(interpolationPoints2, intertialFrame)
        interpolator3 = self.build_all_type_of_interpolator(interpolationPoints3, intertialFrame)

        # P and R
        self.checkAbsPVInterpolationError(interpolationPoints1, 766704.6033758943, 3385.895505018284,
                                          9.503905101141868, 0.0, interpolator1[0])
        self.checkAbsPVInterpolationError(interpolationPoints2, 46190.78568215623, 531.3506621730367,
                                          0.5601906427491941, 0, interpolator2[0])
        self.checkAbsPVInterpolationError(interpolationPoints3, 2787.7069621834926, 55.5146607205871,
                                          0.03372344505743245, 0.0, interpolator3[0])

        # PV and RR
        self.checkAbsPVInterpolationError(interpolationPoints1, 14023.999059896296, 48.022197580401084,
                                          0.16984517369482555, 0.0, interpolator1[1])
        self.checkAbsPVInterpolationError(interpolationPoints2, 16.186825338590722, 0.13418685366189476,
                                          1.898961129289559E-4, 0, interpolator2[1])
        self.checkAbsPVInterpolationError(interpolationPoints3, 0.025110113133073413, 3.5069332429486154E-4,
                                          2.3306042475258594E-7, 0.0, interpolator3[1])

        # PVA and RRR
        self.checkAbsPVInterpolationError(interpolationPoints1, 108.13907262943746, 0.4134494277844817,
                                          0.001389170843175492, 0.0, interpolator1[2])
        self.checkAbsPVInterpolationError(interpolationPoints2, 0.002974408269435121, 2.6937387601886076E-5,
                                          2.051629855188969E-4, 0, interpolator2[2])
        self.checkAbsPVInterpolationError(interpolationPoints3, 0, 0,
                                          1.3779131041190534E-4, 0.0, interpolator3[2])
