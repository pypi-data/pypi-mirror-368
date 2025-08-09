import orekit_jpype as orekit
import jpype

def test_init_vm_args():
    orekit.initVM(vmargs='-verbose:jni')
    assert jpype.isJVMStarted()
