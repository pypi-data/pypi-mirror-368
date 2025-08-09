import orekit_jpype as orekit
import jpype
import os

def test_init_vm_jdk4py():
    # This test will only run if the jdk4py library is installed
    try:
        import jdk4py
        libjvm_path = os.path.join(jdk4py.JAVA_HOME, "lib", "server", "libjvm.so")
        assert os.path.isfile(libjvm_path)

        # We pass the path to JDK via an argument to orekit_jpype (which passes it to jpype)
        orekit.initVM(jvmpath=libjvm_path)
        assert jpype.isJVMStarted()

    except ImportError:
        return
