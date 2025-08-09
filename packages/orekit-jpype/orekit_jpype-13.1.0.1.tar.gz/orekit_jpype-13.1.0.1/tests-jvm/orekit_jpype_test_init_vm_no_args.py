import orekit_jpype as orekit
import jpype

def test_init_vm_no_args():
    orekit.initVM()
    assert jpype.isJVMStarted()
