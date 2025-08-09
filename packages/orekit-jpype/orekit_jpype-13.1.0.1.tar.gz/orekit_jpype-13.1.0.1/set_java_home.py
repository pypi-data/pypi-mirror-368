"""
prints jdk4py's path to JAVA_HOME
call it from bash to write it to an environment variable:
    export JAVA_HOME=`python3 set_java_home.py`
"""

import jdk4py

if __name__ == '__main__':
    print(str(jdk4py.JAVA_HOME))
