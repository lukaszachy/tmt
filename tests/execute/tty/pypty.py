#!/usr/bin/python3

# Run command under pty and in bash. Command is the first and only parameter.
# Usage: python pypty.py COMMAND

import sys
import pty
import os

os.environ["TERM"] = "vt100"
pty.spawn(("/bin/bash", "-c", sys.argv[1]))
