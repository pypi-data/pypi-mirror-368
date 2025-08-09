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
import unittest, sys

from orekit_jpype import initVM
initVM()

from orekit_jpype.pyhelpers import setup_orekit_curdir
setup_orekit_curdir("resources")

from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.hipparchus.ode.nonstiff import AdaptiveStepsizeIntegrator, DormandPrince853Integrator
from org.orekit.bodies import CR3BPFactory
from org.orekit.errors import OrekitException
from org.orekit.frames import Frame
from org.orekit.propagation import SpacecraftState
from org.orekit.propagation.numerical import NumericalPropagator
from org.orekit.propagation.numerical.cr3bp import CR3BPForceModel
from org.orekit.propagation.numerical.cr3bp import STMEquations
from org.orekit.time import AbsoluteDate
from org.orekit.time import TimeScalesFactory
from org.orekit.utils import AbsolutePVCoordinates, LagrangianPoints, PVCoordinates
from org.orekit.orbits import CR3BPDifferentialCorrection, HaloOrbit, LibrationOrbitFamily, LibrationOrbitType, RichardsonExpansion


# Import Python classes

class HaloOrbitTest(unittest.TestCase):

    def test_halo_orbit(self):
        # Python version of the testHaloOrbit method
        # Initialize objects and perform the test
        syst = CR3BPFactory.getEarthMoonCR3BP()
        firstGuess = PVCoordinates(
            Vector3D(0.0, 1.0, 2.0),
            Vector3D(3.0, 4.0, 5.0)
        )
        
        h1 = HaloOrbit(RichardsonExpansion(syst, LagrangianPoints.L1), 8E6, LibrationOrbitFamily.NORTHERN)
        h2 = HaloOrbit(syst, firstGuess, 2.0)
        h3 = HaloOrbit(RichardsonExpansion(syst, LagrangianPoints.L2), 8E6, LibrationOrbitFamily.SOUTHERN)


        orbitalPeriod1 = h1.getOrbitalPeriod()
        orbitalPeriod2 = h2.getOrbitalPeriod()
        orbitalPeriod3 = h3.getOrbitalPeriod()

        # Assert the orbital periods
        self.assertNotAlmostEqual(0.0, orbitalPeriod1, delta=0.5)
        self.assertNotAlmostEqual(0.0, orbitalPeriod3, delta=0.5)
        self.assertAlmostEqual(2.0, orbitalPeriod2, places=15)

        firstGuess1: PVCoordinates = h1.getInitialPV()
        firstGuess2: PVCoordinates = h2.getInitialPV()
        firstGuess3: PVCoordinates = h3.getInitialPV()

        # Assert the initial PV coordinates for h1
        self.assertNotAlmostEqual(0.0, firstGuess1.getPosition().getX(), delta=0.6)
        self.assertAlmostEqual(0.0, firstGuess1.getPosition().getY(), places=15)
        self.assertAlmostEqual(0.0, firstGuess1.getVelocity().getX(), places=15)
        self.assertNotAlmostEqual(0.0, firstGuess1.getVelocity().getY(), delta=0.01)
        self.assertAlmostEqual(0.0, firstGuess1.getVelocity().getZ(), places=15)

        # Assert the initial PV coordinates for h3
        self.assertNotAlmostEqual(0.0, firstGuess3.getPosition().getX(), delta=1)
        self.assertAlmostEqual(0.0, firstGuess3.getPosition().getY(), places=15)
        self.assertAlmostEqual(0.0, firstGuess3.getVelocity().getX(), places=15)
        self.assertNotAlmostEqual(0.0, firstGuess3.getVelocity().getY(), delta=0.01)
        self.assertAlmostEqual(0.0, firstGuess3.getVelocity().getZ(), places=15)

        # Assert the first guess PV coordinates against h2's initial PV
        self.assertAlmostEqual(firstGuess.getPosition().getX(), firstGuess2.getPosition().getX(), places=15)
        self.assertAlmostEqual(firstGuess.getPosition().getY(), firstGuess2.getPosition().getY(), places=15)
        self.assertAlmostEqual(firstGuess.getPosition().getZ(), firstGuess2.getPosition().getZ(), places=15)
        self.assertAlmostEqual(firstGuess.getVelocity().getX(), firstGuess2.getVelocity().getX(), places=15)
        self.assertAlmostEqual(firstGuess.getVelocity().getY(), firstGuess2.getVelocity().getY(), places=15)
        self.assertAlmostEqual(firstGuess.getVelocity().getZ(), firstGuess2.getVelocity().getZ(), places=15)

        
    
    def test_lagrangian_error(self):
        # Example of testing for an exception
        with self.assertRaises(OrekitException):
            syst = CR3BPFactory.getEarthMoonCR3BP()
            # Assuming HaloOrbit construction might raise an OrekitException
            h = HaloOrbit(RichardsonExpansion(syst, LagrangianPoints.L3), 8E6, LibrationOrbitFamily.NORTHERN)
    
    def test_manifolds(self):
        # Simplified example of the testManifolds method
        # Time settings
        initialDate = AbsoluteDate(1996, 6, 25, 0, 0, 0.000, TimeScalesFactory.getUTC())
        syst = CR3BPFactory.getEarthMoonCR3BP()

        syst.getPrimary().getPVCoordinates(initialDate, syst.getSecondary().getInertiallyOrientedFrame())

        frame = syst.getRotatingFrame()

        # Define a Northern Halo orbit around Earth-Moon L1 with a Z-amplitude
        # of 8 000 km
        h = HaloOrbit(RichardsonExpansion(syst, LagrangianPoints.L1), 8E6, LibrationOrbitFamily.SOUTHERN)

        orbitalPeriod = h.getOrbitalPeriod()

        integrationTime = orbitalPeriod * 0.9

        firstGuess = h.getInitialPV()

        initialConditions = CR3BPDifferentialCorrection(firstGuess, syst, orbitalPeriod).compute(LibrationOrbitType.HALO)

        initialAbsPV = AbsolutePVCoordinates(frame, initialDate, initialConditions)

        # Creating the initial spacecraftstate that will be given to the
        # propagator
        initialState = SpacecraftState(initialAbsPV)

        # Integration parameters
        # These parameters are used for the Dormand-Prince integrator, a
        # variable step integrator,
        # these limits prevent the integrator to spend too much time when the
        # equations are too stiff,
        # as well as the reverse situation.
        minStep = 1E-10
        maxstep = 1E-2
        # Tolerances for integrators
        # Used by the integrator to estimate its variable integration step
        positionTolerance = 0.0001
        velocityTolerance = 0.0001
        massTolerance = 1.0e-6
        vecAbsoluteTolerances = [positionTolerance, positionTolerance, positionTolerance,
                                 velocityTolerance, velocityTolerance, velocityTolerance, massTolerance]
        vecRelativeTolerances = [0.0] * len(vecAbsoluteTolerances)

        # Defining the numerical integrator that will be used by the propagator
        integrator = DormandPrince853Integrator(minStep, maxstep, vecAbsoluteTolerances, vecRelativeTolerances)

        stm = STMEquations(syst)
        augmentedInitialState = stm.setInitialPhi(initialState)
        propagator = NumericalPropagator(integrator)
        propagator.setOrbitType(None)
        propagator.setIgnoreCentralAttraction(True)
        propagator.addForceModel(CR3BPForceModel(syst))
        propagator.addAdditionalDerivativesProvider(stm)
        propagator.setInitialState(augmentedInitialState)
        finalState = propagator.propagate(initialDate.shiftedBy(integrationTime))

        initialUnstableManifold = h.getManifolds(finalState, False)
        initialStableManifold = h.getManifolds(finalState, True)

        assert finalState.getPosition().getX() != initialUnstableManifold.getPosition().getX()
        assert finalState.getPosition().getY() != initialUnstableManifold.getPosition().getY()
        assert finalState.getPosition().getZ() != initialUnstableManifold.getPosition().getZ()

        assert finalState.getPosition().getX() != initialStableManifold.getPosition().getX()
        assert finalState.getPosition().getY() != initialStableManifold.getPosition().getY()
        assert finalState.getPosition().getZ() != initialStableManifold.getPosition().getZ()

        pass
    
    def test_differential_correction_error(self):
        # Example of testing for an exception
        with self.assertRaises(OrekitException):
            syst = CR3BPFactory.getEarthMoonCR3BP()
            orbitalPeriod = 1
            firstGuess = PVCoordinates(Vector3D(0.0, 1.0, 2.0), Vector3D(3.0, 4.0, 5.0))
            initialConditions = CR3BPDifferentialCorrection(firstGuess, syst, orbitalPeriod).compute(LibrationOrbitType.HALO)
            print(initialConditions.toString())

    
    def test_stm_error(self):
        with self.assertRaises(OrekitException):
            # Time settings
            initialDate = AbsoluteDate(1996, 6, 25, 0, 0, 0.000, TimeScalesFactory.getUTC())
            syst = CR3BPFactory.getEarthMoonCR3BP()

            frame = syst.getRotatingFrame()

            # Define a Northern Halo orbit around Earth-Moon L1 with a Z-amplitude
            # of 8 000 km
            h = HaloOrbit(RichardsonExpansion(syst, LagrangianPoints.L1), 8E6, LibrationOrbitFamily.SOUTHERN)

            pv = PVCoordinates(Vector3D(0.0, 1.0, 2.0), Vector3D(3.0, 4.0, 5.0))

            initialAbsPV = AbsolutePVCoordinates(frame, initialDate, pv)

            # Creating the initial spacecraftstate that will be given to the
            # propagator
            s = SpacecraftState(initialAbsPV)

            manifold = h.getManifolds(s, True)
            manifold.getMomentum()

if __name__ == '__main__':
    #unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(HaloOrbitTest)
    ret = not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    sys.exit(ret)

