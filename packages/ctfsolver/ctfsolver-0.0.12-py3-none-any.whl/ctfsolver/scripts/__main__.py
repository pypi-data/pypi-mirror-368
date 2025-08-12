"""
Main entry point for the CTF Solver script package.

This module provides functions to run specific submodules of the ctfsolver package
as separate processes using Python's subprocess module. It is intended to be used
as a command-line interface for invoking different functionalities, such as running
the template solver or finding usage information.

It does not care where the script is called from

Functions:
    running(module): Executes the specified module as a subprocess and exits with its return code.
    run_template(): Runs the 'ctfsolver.template' module.
    run_find_usage(): Runs the 'ctfsolver.find_usage' module.


"""

import subprocess
import sys


def running(module):
    result = subprocess.run([sys.executable, "-m", module], check=True)
    sys.exit(result.returncode)


def run_template():
    running("ctfsolver.template")


def run_find_usage():
    running("ctfsolver.find_usage")
