import orekit_jpype
orekit_jpype.initVM()

from orekit_jpype.pyhelpers import setup_orekit_curdir, JArray_double2D, absolutedate_to_datetime, JArray_double1D
setup_orekit_curdir("resources")

from org.orekit.time import AbsoluteDate, TimeScalesFactory
import numpy as np
from datetime import datetime

def test_absolute_date_to_datetime_converter():
    abs_date = AbsoluteDate(2020, 2, 15, 19, 57, 42.698723, TimeScalesFactory.getUTC())
    py_datetime = absolutedate_to_datetime(abs_date)
    assert abs_date.to_datetime() == py_datetime

def test_JConversion_datetime_to_absolute_date():
    py_datetime_expected = datetime(2020, 2, 15, 19, 57, 42, 698723)
    abs_date = AbsoluteDate(py_datetime_expected, 0.0) # This implicitly calls the _JADConversion function in orekit_converters.py
    py_datetime_actual = absolutedate_to_datetime(abs_date)
    assert py_datetime_actual == py_datetime_expected

def test_repr():
    utc_timescale = TimeScalesFactory.getUTC()
    assert utc_timescale.__repr__() == "<UTCScale: UTC>"

def test_2darray_converter():
    np_array_expected = np.array([[5.0, 6.0],
                                  [7.0, 8.0]])
    jarray_2d = JArray_double2D(np_array_expected)

    np_array_actual = jarray_2d.to_numpy()
    assert np.all(np_array_actual == np_array_expected)

def test_2darray_repr():
    np_array_expected = np.array([[5.0, 6.0],
                                  [7.0, 8.0]])
    jarray_2d = JArray_double2D(np_array_expected)
    assert jarray_2d.__repr__() == "<double[][]: [[5. 6.], [7. 8.]]>"

def test_1darray_converter():
    np_array_expected = np.array([1.0, 2.0, 3.0])
    jarray = JArray_double1D(np_array_expected)
    np_array_actual = jarray.to_numpy()
    assert np.all(np_array_actual == np_array_expected)

def test_1darray_repr():
    np_array_expected = np.array([1.0, 2.0, 3.0])
    jarray = JArray_double1D(np_array_expected)
    assert jarray.__repr__() == "<double[]: [1. 2. 3.]>"
