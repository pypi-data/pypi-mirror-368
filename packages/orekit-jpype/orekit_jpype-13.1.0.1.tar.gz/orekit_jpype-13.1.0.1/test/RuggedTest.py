from orekit_jpype import initVM
initVM()

from orekit_jpype.pyhelpers import setup_orekit_curdir, datetime_to_absolutedate
setup_orekit_curdir("resources")

import unittest
import pytest
import datetime
import numpy as np
from typing import Tuple

from java.util import ArrayList
from org.hipparchus.geometry.euclidean.threed import Vector3D, Rotation
from org.orekit.rugged.los import LOSBuilder
from org.orekit.rugged.linesensor import LinearLineDatation, LineSensor
from org.orekit.frames import FramesFactory
from org.orekit.utils import IERSConventions, TimeStampedPVCoordinates, CartesianDerivativesFilter, AngularDerivativesFilter, AbsolutePVCoordinates
from org.orekit.rugged.api import RuggedBuilder, AlgorithmId, Rugged
from org.orekit.models.earth import ReferenceEllipsoid
from org.orekit.attitudes import AttitudeProvider, FrameAlignedProvider
from org.orekit.propagation import Propagator
from org.orekit.propagation.analytical import KeplerianPropagator
from org.orekit.orbits import CartesianOrbit
from org.orekit.propagation.analytical.tle import TLE, SGP4
from org.orekit.time import AbsoluteDate
from org.orekit.utils import Constants
from org.orekit.bodies import GeodeticPoint


class RuggedTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(RuggedTest, self).__init__(*args, **kwargs)

        self.fov_x = 0.0572 # half angle, deg
        self.fov_y = 0.0761 # half angle, deg

        self.tod = FramesFactory.getTOD(IERSConventions.IERS_2010, True)
        self.itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
        self.wgs84_ellipsoid = ReferenceEllipsoid.getWgs84(self.itrf)

        self.t_step = 1.0
        self.overshoot_tolerance = 1.0
        self.n_interpolation_neighbours = 2

    def build_line_sensor(self, line_epoch: AbsoluteDate) -> LineSensor:
        """
        Builds a LineSensor object with only one viewing direction,
        along the +Z axis of the spacecraft
        """
        viewing_directions = ArrayList()
        los_vec_SAT = Vector3D(
                0.0,
                0.0,
                1.0
            )
        viewing_directions.add(los_vec_SAT)

        line_of_sight = LOSBuilder(viewing_directions).build()

        line_datation = LinearLineDatation(line_epoch,
                                           0.0,
                                           1e3)

        return LineSensor("LineSensor", line_datation, Vector3D.ZERO, line_of_sight)

    def build_propagator(self,
                         timestamp: datetime.datetime,
                         pos_TOD,
                         vel_TOD,
                         att_provider: AttitudeProvider) -> Propagator:
        """
        Build a Kepler propagator from only one datapoint with position/velocity/attitude/rate
        parameters:
            timestamp: datetime
            pos_TOD: 3*1 numpy array containing position in TOD frame in meters
            vel_TOD: 3*1 numpy array containing velocity in TOD frame in m/s
            att_provider: AttitudeProvider
        """
        timestamped_PV = TimeStampedPVCoordinates(datetime_to_absolutedate(timestamp),
                                                  Vector3D(pos_TOD.tolist()),
                                                  Vector3D(vel_TOD.tolist())
                                                  )

        orbit = CartesianOrbit(timestamped_PV,
                               self.tod,
                               Constants.WGS84_EARTH_MU)

        return KeplerianPropagator(orbit, att_provider)

    def build_rugged(self, propagator: Propagator, min_date: AbsoluteDate, max_date: AbsoluteDate,
                     line_sensor: LineSensor) -> Rugged:
        """
        Build a Rugged instance from the given Ephemeris propagator and only one line sensor
        Without DEM, only with ellipsoid, and with all other settings to default
        """
        rugged_builder = RuggedBuilder()

        rugged_builder.setAlgorithm(AlgorithmId.IGNORE_DEM_USE_ELLIPSOID)
        rugged_builder.setEllipsoid(self.wgs84_ellipsoid)

        rugged_builder.setTimeSpan(min_date,
                                   max_date,
                                   self.t_step,
                                   self.overshoot_tolerance
                                   )

        pos_derivative_filter = CartesianDerivativesFilter.USE_PV
        angular_derivative_filter = AngularDerivativesFilter.USE_RR

        rugged_builder.setTrajectory(self.t_step,
                                     self.n_interpolation_neighbours,
                                     pos_derivative_filter,
                                     angular_derivative_filter,
                                     propagator
                                     )

        rugged_builder.addLineSensor(line_sensor)

        return rugged_builder.build()

    def build_frame_aligned_provider(self, q_TODfromSAT) -> AttitudeProvider:
        rotation = Rotation(float(q_TODfromSAT[0]),
                            float(q_TODfromSAT[1]),
                            float(q_TODfromSAT[2]),
                            float(q_TODfromSAT[3]),
                            True)
        return FrameAlignedProvider(rotation, self.tod)

    def build_tle_propagator(self, att_provider: AttitudeProvider,
                             tle_line1: str, tle_line2: str) -> Propagator:
        tle = TLE(tle_line1, tle_line2)
        return SGP4(tle, att_provider, 50.0)

    def direct_location(self, timestamp: datetime.datetime, propagator: Propagator) -> GeodeticPoint:
        absolute_date = datetime_to_absolutedate(timestamp)
        min_date = absolute_date.shiftedBy(-self.t_step)
        max_date = absolute_date.shiftedBy(self.t_step)

        line_sensor = self.build_line_sensor(line_epoch=min_date)

        rugged = self.build_rugged(propagator=propagator,
                                   min_date=min_date,
                                   max_date=max_date,
                                   line_sensor=line_sensor)

        los = line_sensor.getLOS(absolute_date, 0)
        return rugged.directLocation(absolute_date, Vector3D.ZERO, los)


    def test_rugged_direct_location_single_pva_point(self):
        """
        Performs a basic direct location from a single data point (position, velocity, attitude)
        This test is not super accurate but is only here to test that Rugged is not broken
        """

        """
        Creating an Ephemeris propagator from example telemetry data from the TUBIN satellite
        from TU Berlin
        """
        timestamp = datetime.datetime(2023, 8, 17, 16, 6, 26, 400000)

        inertial_att_provider = self.build_frame_aligned_provider(
            q_TODfromSAT=np.array([0.1288, 0.85362673, -0.12312595, 0.48946089])
            )

        bounded_prop = self.build_propagator(
            timestamp=timestamp,
            pos_TOD=np.array([-5984085., -831225., 3291501.75]),
            vel_TOD=np.array([-3744.86083984, 638.70556641, -6598.59521484]),
            att_provider=inertial_att_provider
        )

        geodetic_point = self.direct_location(
            timestamp=timestamp,
            propagator=bounded_prop
        )

        """
        The coordinates should approximately correspond to Tenerife
        """
        assert np.rad2deg(geodetic_point.getLatitude()) == pytest.approx(28.5, abs=1.0)
        assert np.rad2deg(geodetic_point.getLongitude()) == pytest.approx(-17.0, abs=1.0)


    def test_rugged_direct_location_from_tle(self):
        """
        Performs a basic direct location from Two-Line Elements data
        and attitude telemetry from the TUBIN satellite from TU Berlin
        This test is not super accurate but is only here to test that Rugged is not broken
        """

        """
        Creating a propagator from a TLE
        """
        timestamp = datetime.datetime(2023, 8, 17, 16, 6, 26, 400000)

        inertial_att_provider = self.build_frame_aligned_provider(
            q_TODfromSAT=np.array([0.1288, 0.85362673, -0.12312595, 0.48946089])
            )

        propagator = self.build_tle_propagator(
            inertial_att_provider,
            tle_line1="1 48900U 21059X   23229.44616644  .00010250  00000-0  47112-3 0  9997",
            tle_line2="2 48900  97.6079   3.5060 0009943  72.3812 287.8508 15.20521326118480"
        )

        geodetic_point = self.direct_location(
            timestamp=timestamp,
            propagator=propagator
        )

        """
        The coordinates should approximately correspond to Tenerife
        """
        assert np.rad2deg(geodetic_point.getLatitude()) == pytest.approx(28.5, abs=1.0)
        assert np.rad2deg(geodetic_point.getLongitude()) == pytest.approx(-17.0, abs=1.0)
