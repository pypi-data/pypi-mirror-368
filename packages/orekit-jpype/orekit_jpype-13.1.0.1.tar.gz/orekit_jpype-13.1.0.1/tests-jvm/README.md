# Orekit Jpype JVM tests

As Jpype does not allow restarting the JVM, when pytest runs all tests in a sequence, the JVM will be already started and therefore we cannot test the behaviour of orekit_jpype's `startJVM` method depending on its input arguments.

As a workaround, this folder contains several test files containing one call to `startJVM` each, intended to be called separately from `pytest`. Do not call `pytest` on this whole folder, there is no `pytest.ini` anyways so it won't collect any test case :) .
