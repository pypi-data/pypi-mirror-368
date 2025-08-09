import orekit_jpype as orekit
import pytest

def test_init_vm_invalid_classpath():
    with pytest.raises(FileNotFoundError) as exc_info:
        # This call is supposed to fail because we give a non existing path
        orekit.initVM(additional_classpaths=["non_existing_path"])
