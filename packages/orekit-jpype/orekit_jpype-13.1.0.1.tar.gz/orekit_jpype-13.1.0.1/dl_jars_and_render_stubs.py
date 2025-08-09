# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "stubgenj",
# ]
# ///

from pathlib import Path
import jpype
import stubgenj
import shutil
import sys
from subprocess import PIPE, run

jar_folder = Path("orekit_jpype") / "jars"
javadoc_jar_folder = Path("orekit_jpype") / "javadoc-jars"
stubs_folders = ["java-stubs", "jpype-stubs", "org-stubs"]

if __name__ == '__main__':
    # First removing all old JARs to avoid multiple versions of the same JAR
    if jar_folder.exists() and jar_folder.is_dir():
        shutil.rmtree(jar_folder)
    if javadoc_jar_folder.exists() and javadoc_jar_folder.is_dir():
        shutil.rmtree(javadoc_jar_folder)

    # Calling maven to download the JARs. Maven must be installed on your system
    result = run(["mvn", "dependency:copy"], universal_newlines=True)

    jar_list = list(map(str, jar_folder.glob('**/*.jar')))
    javadoc_jar_list = list(map(str, javadoc_jar_folder.glob('**/*.jar')))

    if result.returncode == 0:
        print(f"""Successfully downloaded following JARs:
              - normal JARs: {jar_list}
              - javadoc JARs: {javadoc_jar_list}
************* Now generating stubs *************
              """)
    else:
        print(f"Maven called returned non-zero exit code {result.returncode}")
        sys.exit(result.returncode)

    # Removing old stubs folders
    for stub_folder in stubs_folders:
        stub_path = Path(stub_folder)
        if stub_path.exists() and stub_path.is_dir():
            shutil.rmtree(stub_path)

    # Generating stubs
    classpath = jar_list + javadoc_jar_list
    jpype.startJVM(classpath=classpath, convertStrings=True)

    import jpype.imports  # noqa
    import org.orekit  # noqa
    import org.hipparchus  # noqa
    import java  # noqa

    stubgenj.generateJavaStubs([java, org.orekit, org.hipparchus],
                                useStubsSuffix=True)


# python -m stubgenj --convert-strings --classpath "orekit_jpype/jars/*.jar" org.orekit  org.hipparchus java jpype
