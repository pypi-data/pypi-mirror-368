# -*- coding: utf-8 -*-
# pylint: disable=W,C
"""
Horizon Robotics Development Kit.
All rights reserved.
"""

import os
import sys
from os import path

# Entry point functions for console programs
#


def main():
    realpath = path.realpath(path.join(path.dirname(__file__), "../bin/hbdk-disas"))
    if len(sys.argv) == 2 and sys.argv[1] == "--where":
        print(realpath, flush=True)
    else:
        os.execv(realpath, [realpath] + sys.argv[1:])

