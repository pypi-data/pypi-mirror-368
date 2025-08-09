import orekit_jpype
orekit_jpype.initVM()

from orekit_jpype.pyhelpers import JArray_double2D, download_orekit_data_curdir, clear_factories, to_elevationmask, setup_orekit_data

from org.orekit.bodies import CelestialBodyFactory
from org.orekit.errors import OrekitException

from java.io import File

import os
import numpy as np
import pytest

def check_orekit_data_valid():
    from org.orekit.time import TimeScalesFactory  # noqa: E402
    utc = TimeScalesFactory.getUTC()
    last_leap_second = utc.getLastKnownLeapSecond()
    return last_leap_second.getComponents(utc).getDate().getYear() >= 2016

def test_setup_orekit_data_from_folder():
    setup_orekit_data(filenames="resources", from_pip_library=False)

    assert check_orekit_data_valid()

    clear_factories()

def test_setup_orekit_data_from_invalid_folder():
    filename = "wrong_folder"
    datafile = File(filename)
    assert datafile.exists() == False

    with pytest.raises(FileNotFoundError) as e:
        setup_orekit_data(filenames=filename, from_pip_library=False)
    
    assert str(e.value) == datafile.getAbsolutePath()
    clear_factories()

def test_setup_orekit_data_default_args():
    """
    This test case has two different behaviours depending if the§ orekitdata library is installed or not
    """
    try:
        import orekitdata
        setup_orekit_data()
        assert check_orekit_data_valid()
    except ModuleNotFoundError:
        assert True
        with pytest.raises(OrekitException) as exc_info:
            with pytest.raises(FileNotFoundError) as e:
                setup_orekit_data()
            # This call is supposed to fail because no more ephemerides are loaded
            check_orekit_data_valid()
        assert exc_info.value.args[0] == 'no IERS UTC-TAI history data loaded'

    clear_factories()

def test_setup_orekit_data_from_library():
    """
    This test case has two different behaviours depending if the orekitdata library is installed or not
    """
    try:
        import orekitdata
        setup_orekit_data(filenames=None, from_pip_library=True)
        assert check_orekit_data_valid()
    except ModuleNotFoundError:
        assert True
        with pytest.raises(OrekitException) as exc_info:
            with pytest.raises(FileNotFoundError) as e:
                setup_orekit_data(filenames=None, from_pip_library=True)
            # This call is supposed to fail because no more ephemerides are loaded
            check_orekit_data_valid()
        assert exc_info.value.args[0] == 'no IERS UTC-TAI history data loaded'

    clear_factories()

def test_download_and_setup_orekit_data_from_zip():
    filename = "orekit-data-test.zip"
    download_orekit_data_curdir(filename=filename)
    assert os.path.exists(filename) and os.path.isfile(filename)

    setup_orekit_data(filenames=filename, from_pip_library=False)

    assert check_orekit_data_valid()

    # Delete file at the end
    if os.path.exists(filename):
        os.remove(filename)

    clear_factories()

def test_JArray_double2D():
    np_array_expected = np.array([[5.0, 6.0],
                                  [7.0, 8.0]])
    jarray_2d = JArray_double2D(np_array_expected)
    np_array_actual = np.array(jarray_2d)
    assert np.all(np_array_expected == np_array_actual)

def test_clear_factories():
    setup_orekit_data(filenames="resources", from_pip_library=False)

    earth = CelestialBodyFactory.getEarth()

    clear_factories()

    with pytest.raises(OrekitException) as exc_info:
        # This call is supposed to fail because no more ephemerides are loaded
        CelestialBodyFactory.getEarth()
    assert exc_info.value.args[0] == 'no JPL ephemerides binary files found'

    # Setting up again orekit data for next tests...
    setup_orekit_data(filenames="resources", from_pip_library=False)

def test_elevation_mask():
    az = [0, 90, 180, 270]
    el = [5,10,8,5]
    el_mask = to_elevationmask(az=az, el=el)

    for i in range(0, len(az)):
        az_deg = az[i]
        el_expected_deg = el[i]
        assert np.rad2deg(el_mask.getElevation(np.deg2rad(az_deg))) == el_expected_deg
