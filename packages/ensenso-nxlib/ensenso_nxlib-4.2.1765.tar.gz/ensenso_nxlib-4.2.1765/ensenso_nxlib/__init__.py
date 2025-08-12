# This is a workaround to create an alias for the nxlib package with the old
# package name ensenso_nxlib.
# https://stackoverflow.com/questions/56559817/how-do-i-alias-a-python-module-at-packaging-time

import sys

import nxlib
from nxlib import *


sys.modules["ensenso_nxlib"] = nxlib
