import orekit_jpype as orekit
import jpype
import os

def test_init_vm_with_extra_jars():
    orekit.initVM(additional_classpaths=[os.path.join("resources", "jars", "xml-commons-resolver-1.2.jar")])
    assert jpype.isJVMStarted()

    # We try instantiating a random class of the xml-commons-resolver library
    from org.apache.xml.resolver import Catalog
    catalog = Catalog()
    assert isinstance(catalog, Catalog)
