import orekit_jpype as orekit
import jpype
import os
import pytest

def test_init_vm_wrong_jvm_path():
    libjvm_path = "wrong_path_to_libjvm_file"
    assert os.path.isfile(libjvm_path) == False

    if not jpype.isJVMStarted():
        with pytest.raises(OSError) as exc_info:
            # This call is supposed to fail becaue we give a wrong path to the libjvm library file
            orekit.initVM(jvmpath=libjvm_path)
        assert exc_info.value.args[1].startswith('JVM DLL not found')
