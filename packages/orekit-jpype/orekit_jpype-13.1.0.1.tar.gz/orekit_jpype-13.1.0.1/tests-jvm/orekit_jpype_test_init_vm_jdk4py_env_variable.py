import orekit_jpype as orekit
import jpype
import os

def test_init_vm_jdk4py_env_variable():
    # This test will only run if the jdk4py library is installed
    try:
        import jdk4py
        # We pass the path to JDK via environment variable
        os.environ["JAVA_HOME"] = str(jdk4py.JAVA_HOME)

        orekit.initVM()
        assert jpype.isJVMStarted()

    except ImportError:
        return
