# selenium_web_automation_utils/compatibility.py
import sys
import platform

_py_ver = tuple(map(int, platform.python_version_tuple()))
if _py_ver >= (3, 12):
    # setuptools bundles distutils for backward-compatibility
    from setuptools._distutils import version as _dv
    sys.modules["distutils.version"] = _dv
