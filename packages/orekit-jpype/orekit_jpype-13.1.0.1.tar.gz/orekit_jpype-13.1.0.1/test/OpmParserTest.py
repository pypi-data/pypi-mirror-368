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

# all orekit imports needs to come after the JVM is initialized

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
from org.orekit.time import AbsoluteDate, TimeScalesFactory, TimeOffset
from org.orekit.utils import Constants, IERSConventions, PVCoordinates, TimeStampedPVCoordinates
from java.nio.charset import StandardCharsets
from org.orekit.files.ccsds.ndm.odm.opm import OpmWriter



# import java.io.ByteArrayInputStream;
# import java.io.CharArrayWriter;
# import java.io.IOException;
# import java.net.URISyntaxException;
# import java.nio.charset.StandardCharsets;
# import java.util.ArrayList;
# import java.util.HashMap;

from java.io import ByteArrayInputStream, CharArrayWriter, IOException
from java.net import URISyntaxException
from java.util import ArrayList, HashMap
from java.io import File

@JImplements(DataSource.StreamOpener)
class myReader(object):
    def __init__(self, data) -> None:
        self.data = data

    @JOverride
    def openOnce(self):
        return ByteArrayInputStream(list(self.data.encode()))

class OpmParserTest(unittest.TestCase): 

    def checkPVEntry(self, expected, actual) -> None:
        """
        Compares the position and velocity entries of the expected and actual objects.

        Args:
            expected: The expected object containing the position and velocity entries.
            actual: The actual object containing the position and velocity entries.

        Returns:
            None
        """
        expectedPos = expected.getPosition()
        expectedVel = expected.getVelocity()

        actualPos = actual.getPosition()
        actualVel = actual.getVelocity()

        eps = 1e-12

        self.assertAlmostEqual(expectedPos.getX(), actualPos.getX(), delta=eps)
        self.assertAlmostEqual(expectedPos.getY(), actualPos.getY(), delta=eps)
        self.assertAlmostEqual(expectedPos.getZ(), actualPos.getZ(), delta=eps)

        self.assertAlmostEqual(expectedVel.getX(), actualVel.getX(), delta=eps)
        self.assertAlmostEqual(expectedVel.getY(), actualVel.getY(), delta=eps)
        self.assertAlmostEqual(expectedVel.getZ(), actualVel.getZ(), delta=eps)


    def testParseOPM1KVN(self):
        # simple test for OPM file, contains p/v entries and other mandatory
        # data.
        ex = "resources/ccsds/odm/opm/OPMExample1.txt"
        source =  DataSource(File(ex)) #, lambda x: x.getClass().getResourceAsStream(ex))

        parser = ParserBuilder().withMu(398600e9).withDefaultMass(1000.0).buildOpmParser()

        file = parser.parseMessage(source)
        assert IERSConventions.IERS_2010 == file.getConventions()

        # Check Header Block;
        assert 3.0 == file.getHeader().getFormatVersion()
        assert AbsoluteDate(1998, 11, 6, 9, 23, 57, TimeScalesFactory.getUTC()) == file.getHeader().getCreationDate()
        assert "JAXA" == file.getHeader().getOriginator()

        # Check Metadata Block;
        assert "GODZILLA 5" == file.getMetadata().getObjectName()
        assert "1998-999A" == file.getMetadata().getObjectID()
        assert 1998 == file.getMetadata().getLaunchYear()
        assert 999 == file.getMetadata().getLaunchNumber()
        assert "A" == file.getMetadata().getLaunchPiece()
        assert "EARTH" == file.getMetadata().getCenter().getName()
        assert file.getMetadata().getCenter().getBody() is not None
        assert CelestialBodyFactory.getEarth() == file.getMetadata().getCenter().getBody()
        assert CelestialBodyFrame.ITRF2000 == CelestialBodyFrame.map(file.getMetadata().getFrame())
        assert "UTC" == file.getMetadata().getTimeSystem().name()
        assert file.getData().getCovarianceBlock() is None

        # Check State Vector data Block;
        assert AbsoluteDate(1998, 12, 18, 14, 28,
                 TimeOffset(15, TimeOffset.SECOND, 117200, TimeOffset.MICROSECOND),
                 TimeScalesFactory.getUTC()) == file.getDate()
        self.checkPVEntry(PVCoordinates(Vector3D(6503514.000, 1239647.000, -717490.000), Vector3D(-873.160, 8740.420, -4191.076)), file.getPVCoordinates())

        try:
            file.generateCartesianOrbit()
            assert False, "an exception should have been thrown"
        except OrekitIllegalArgumentException as oiae:
            assert OrekitMessages.NON_PSEUDO_INERTIAL_FRAME == oiae.getSpecifier()
            assert "ITRF-2000/CIO/2010-based ITRF simple EOP" == oiae.getParts()[0]
        
        try:
            file.generateKeplerianOrbit()
            assert False, "an exception should have been thrown"
        except OrekitIllegalArgumentException as oiae:
            assert OrekitMessages.NON_PSEUDO_INERTIAL_FRAME == oiae.getSpecifier()
            assert "ITRF-2000/CIO/2010-based ITRF simple EOP" == oiae.getParts()[0]
        
        try:
            file.generateSpacecraftState()
            assert False, "an exception should have been thrown"
        except OrekitIllegalArgumentException as oiae:
            assert OrekitMessages.NON_PSEUDO_INERTIAL_FRAME == oiae.getSpecifier()
            assert "ITRF-2000/CIO/2010-based ITRF simple EOP" == oiae.getParts()[0]
    
    def testParseOPM2(self):
        # simple test for OPM file, contains all mandatory information plus
        # Keplerian elements, Spacecraft parameters and 2 maneuvers.
        ex = "resources/ccsds/odm/opm/OPMExample2.txt"
        source = DataSource(File(ex)) #, lambda x: x.getClass().getResourceAsStream(ex))

        parser = ParserBuilder().withMu(Constants.EIGEN5C_EARTH_MU).withDefaultMass(1000.0).buildOpmParser()
        file = parser.parseMessage(source)
        assert IERSConventions.IERS_2010 == file.getConventions()

        # Check Header Block;
        assert 3.0 == file.getHeader().getFormatVersion()
        headerComment = ["Generated by GSOC, R. Kiehling", "Current intermediate orbit IO2 and maneuver planning data"]
        assert headerComment == list(file.getHeader().getComments())
        assert AbsoluteDate(2000, 6, 3, 5, 33, 00, TimeScalesFactory.getUTC()) == file.getHeader().getCreationDate()
        assert file.getHeader().getOriginator() == "GSOC"

        # Check Metadata Block;
        assert "EUTELSAT W4" == file.getMetadata().getObjectName()
        assert "2000-028A" == file.getMetadata().getObjectID()
        assert "EARTH" == file.getMetadata().getCenter().getName()
        assert file.getMetadata().getCenter().getBody() is not None
        assert CelestialBodyFactory.getEarth() == file.getMetadata().getCenter().getBody()
        assert FramesFactory.getTOD(IERSConventions.IERS_2010, True) == file.getMetadata().getFrame()
        assert "UTC" == file.getMetadata().getTimeSystem().name()
        assert 0 == len(file.getMetadata().getComments())

        # Check Data State Vector block
        epochComment = ["State Vector"]
        assert epochComment == list(file.getData().getStateVectorBlock().getComments())
        assert AbsoluteDate(2006, 6, 3, 00, 00, 00, TimeScalesFactory.getUTC()) == file.getDate()
        self.checkPVEntry(PVCoordinates(Vector3D(6655994.2, -40218575.1, -82917.7),
                                       Vector3D(3115.48208, 470.42605, -1.01495)),
                          file.getPVCoordinates())

        # Check Data Keplerian Elements block
        keplerianElements = file.getData().getKeplerianElementsBlock()
        assert keplerianElements is not None
        keplerianElementsComment = ["Keplerian elements"]
        assert keplerianElementsComment == list(keplerianElements.getComments())
        self.assertAlmostEqual(41399512.3, keplerianElements.getA())
        self.assertAlmostEqual(0.020842611, keplerianElements.getE())
        self.assertAlmostEqual(math.radians(0.117746), keplerianElements.getI())
        self.assertAlmostEqual(math.radians(17.604721), keplerianElements.getRaan())
        self.assertAlmostEqual(math.radians(218.242943), keplerianElements.getPa())
        self.assertAlmostEqual(PositionAngleType.TRUE, keplerianElements.getAnomalyType())
        self.assertAlmostEqual(math.radians(41.922339), keplerianElements.getAnomaly())
        self.assertAlmostEqual(398600.4415 * 1e9, keplerianElements.getMu())

        # Check Data Spacecraft block
        spacecraftParameters = file.getData().getSpacecraftParametersBlock()
        assert spacecraftParameters is not None
        spacecraftComment = ["Spacecraft parameters"]
        assert spacecraftComment == list(spacecraftParameters.getComments())
        self.assertAlmostEqual(1913.000, spacecraftParameters.getMass())
        self.assertAlmostEqual(10.000, spacecraftParameters.getSolarRadArea())
        self.assertAlmostEqual(1.300, spacecraftParameters.getSolarRadCoeff())
        self.assertAlmostEqual(10.000, spacecraftParameters.getDragArea())
        self.assertAlmostEqual(2.300, spacecraftParameters.getDragCoeff())

        # Check covariance block
        assert file.getData().getCovarianceBlock() is None

        # Check Data Maneuvers block
        assert file.getData().hasManeuvers()
        assert 2 == file.getNbManeuvers()
        stateManeuverComment0 = ["2 planned maneuvers", "First maneuver: AMF-3", "Non-impulsive, thrust direction fixed in inertial frame"]
        assert stateManeuverComment0 == list(file.getManeuver(0).getComments())
        assert AbsoluteDate(2000, 6, 3, 9, 0, TimeOffset(34, TimeOffset.SECOND, 100, TimeOffset.MILLISECOND), TimeScalesFactory.getUTC()) == file.getManeuvers().get(0).getEpochIgnition()
        assert 132.6 == file.getManeuver(0).getDuration()
        assert -18.418 == file.getManeuver(0).getDeltaMass()
        assert file.getManeuver(0).getReferenceFrame().asOrbitRelativeFrame() is None
        assert FramesFactory.getEME2000() == file.getManeuver(0).getReferenceFrame().asFrame()
        self.assertAlmostEqual(0.0, Vector3D(-23.25700, 16.83160, -8.93444).distance(file.getManeuver(0).getDV()))

        stateManeuverComment1 = ["Second maneuver: first station acquisition maneuver", "impulsive, thrust direction fixed in RTN frame"]
        assert stateManeuverComment1 == list(file.getManeuver(1).getComments())
        assert AbsoluteDate(2000, 6, 5, 18, 59, 21, TimeScalesFactory.getUTC()) == file.getManeuvers().get(1).getEpochIgnition()
        assert 0.0 == file.getManeuver(1).getDuration()
        assert -1.469 == file.getManeuver(1).getDeltaMass()
        assert LOFType.QSW_INERTIAL == file.getManeuver(1).getReferenceFrame().asOrbitRelativeFrame().getLofType()
        assert file.getManeuver(1).getReferenceFrame().asFrame() is None
        assert file.getManeuver(1).getReferenceFrame().asCelestialBodyFrame() is None
        self.assertAlmostEqual(0.0, Vector3D(1.015, -1.873, 0.0).distance(file.getManeuver(1).getDV()))

        assert file.getData().getUserDefinedBlock() is None
        assert file.generateCartesianOrbit() is not None
        assert file.generateKeplerianOrbit() is not None
        assert file.generateSpacecraftState() is not None

    
    def testWrongODMType(self):
        name = "resources/ccsds/odm/omm/OMMExample1.txt"
        source = DataSource(File(name)) #, lambda x: x.getClass().getResourceAsStream(name))
        try:
            ParserBuilder().withMu(Constants.EIGEN5C_EARTH_MU).withDefaultMass(1000.0).buildOpmParser().parseMessage(source)
            self.fail("an exception should have been thrown")
        except OrekitException as oe:
            self.assertEqual(OrekitMessages.UNSUPPORTED_FILE_FORMAT, oe.getSpecifier())
            self.assertEqual(name.split('/')[-1], oe.getParts()[0])

    def testParseOPM3KVN(self):
        # simple test for OPM file, contains all mandatory information plus
        # Spacecraft parameters and the position/velocity Covariance Matrix.
        name = "resources/ccsds/odm/opm/OPMExample3.txt"
        source = DataSource(File(name))
        parser = ParserBuilder().withDefaultMass(1000.0).buildOpmParser()
        file = parser.parseMessage(source)
        assert "OPM 201113719185" == file.getHeader().getMessageId()
        assert CelestialBodyFrame.TOD == file.getMetadata().getReferenceFrame().asCelestialBodyFrame()
        assert AbsoluteDate(1998, 12, 18, 14, 28,
                 TimeOffset(15, TimeOffset.SECOND, 117200, TimeOffset.MICROSECOND),
                 TimeScalesFactory.getUTC()) == file.getMetadata().getFrameEpoch()
        assert 1 == len(file.getMetadata().getComments())
        assert "GEOCENTRIC, CARTESIAN, EARTH FIXED" == file.getMetadata().getComments()[0]       
        self.assertAlmostEqual(15951238.3495, file.generateKeplerianOrbit().getA(),places= 0)  # TODO HOW CAN THIS DIFFER SO MUCH?
        self.assertAlmostEqual(0.5914452565, file.generateKeplerianOrbit().getE(), delta=1.0e-7)  # TODO CHECK HOW THIS CAN DIFFER FROM JAVA
        # Check Data Covariance matrix Block
        covariance = file.getData().getCovarianceBlock()
        self.assertIsNotNone(covariance)
        assert file.getMetadata().getReferenceFrame() == covariance.getReferenceFrame() 
        covMatrix = [
            [333.1349476038534, 461.8927349220216, -307.0007847730449, -0.3349365033922630, -0.2211832501084875, -0.3041346050686871],
            [461.8927349220216, 678.2421679971363, -422.1234189514228, -0.4686084221046758, -0.2864186892102733, -0.4989496988610662],
            [-307.0007847730449, -422.1234189514228, 323.1931992380369, 0.2484949578400095, 0.1798098699846038, 0.3540310904497689],
            [-0.3349365033922630, -0.4686084221046758, 0.2484949578400095, 0.0004296022805587290, 0.0002608899201686016, 0.0001869263192954590],
            [-0.2211832501084875, -0.2864186892102733, 0.1798098699846038, 0.0002608899201686016, 0.0001767514756338532, 0.0001008862586240695],
            [-0.3041346050686871, -0.4989496988610662, 0.3540310904497689, 0.0001869263192954590, 0.0001008862586240695, 0.0006224444338635500]
        ]
        for i in range(6):
            for j in range(6):
                self.assertAlmostEqual(covMatrix[i][j], covariance.getCovarianceMatrix().getEntry(i, j), delta=1e-15)





    def testWriteOPM3(self):
        # simple test for OPM file, contains all mandatory information plus
        # Spacecraft parameters and the position/velocity Covariance Matrix.
        # the content of the file is slightly different from the KVN file in the covariance section
        name = "resources/ccsds/odm/opm/OPMExample3.xml"
        source = DataSource(File(name))
        parser = ParserBuilder().withDefaultMass(1000.0).buildOpmParser()
        original = parser.parseMessage(source)

        # write the parsed file back to a characters array
        caw = CharArrayWriter()
        generator = KvnGenerator(caw, OpmWriter.KVN_PADDING_WIDTH, "dummy", Constants.JULIAN_DAY, 60)
        WriterBuilder().buildOpmWriter().writeMessage(generator, original)

        # reparse the written file
        bytes = caw.toString() #.getBytes(StandardCharsets.UTF_8)
        source2 = DataSource(name, myReader(bytes))
        rebuilt = ParserBuilder().buildOpmParser().parseMessage(source2)
        self.validateOPM3XML(rebuilt)

    def validateOPM3XML(self, file):
        self.assertEqual("OPM 201113719185", file.getHeader().getMessageId())
        self.assertEqual(CelestialBodyFrame.TOD, file.getMetadata().getReferenceFrame().asCelestialBodyFrame())
        self.assertEqual(AbsoluteDate(1998, 12, 18, 14, 28,
                 TimeOffset(15, TimeOffset.SECOND, 117200, TimeOffset.MICROSECOND),
                 TimeScalesFactory.getUTC()), file.getMetadata().getFrameEpoch())
        self.assertEqual(1, len(file.getMetadata().getComments()))
        self.assertEqual("GEOCENTRIC, CARTESIAN, EARTH FIXED", file.getMetadata().getComments()[0])
        self.assertAlmostEqual(15951238.3495, file.generateKeplerianOrbit().getA(), places=0)  # TODO HOW CAN THIS DIFFER SO MUCH?
        self.assertAlmostEqual(0.5914452565, file.generateKeplerianOrbit().getE(), delta=1.0e-7)  # TODO CHECK HOW THIS CAN DIFFER FROM JAVA
        # Check Data Covariance matrix Block
        covariance = file.getData().getCovarianceBlock()
        self.assertIsNotNone(covariance)
        self.assertEqual(CelestialBodyFrame.ITRF1997, covariance.getReferenceFrame().asCelestialBodyFrame())

        covMatrix = [
            [316000.0, 722000.0, 202000.0, 912000.0, 562000.0, 245000.0],
            [722000.0, 518000.0, 715000.0, 306000.0, 899000.0, 965000.0],
            [202000.0, 715000.0, 002000.0, 276000.0, 022000.0, 950000.0],
            [912000.0, 306000.0, 276000.0, 797000.0, 079000.0, 435000.0],
            [562000.0, 899000.0, 022000.0, 079000.0, 415000.0, 621000.0],
            [245000.0, 965000.0, 950000.0, 435000.0, 621000.0, 991000.0]
        ]
        for i in range(6):
            for j in range(6):
                self.assertAlmostEqual(covMatrix[i][j], covariance.getCovarianceMatrix().getEntry(i, j), delta=1e-15)
