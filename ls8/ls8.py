#!/usr/bin/env python3

"""Main."""

import sys
import os
from cpu import *


if len(sys.argv) != 2:
    print("Usage: Please load a file", file=sys.stderr)
    sys.exit(1)

script_dir = os.path.dirname(__file__)

# argument should be file path, e.g. ./example/foo.bar
file_path = os.path.join(script_dir, sys.argv[1])

cpu = CPU()

cpu.load(sys.argv[1])
cpu.run()
