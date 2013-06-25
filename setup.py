__author__ = 'jurek'
import sys
from cx_Freeze import setup,Executable
build_exe_options = {"packages":["os"],"excludes":["PyQt"]}
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="LanTransfer",
      version="0.1",
      description="Lan Transfer program",
      executables = [Executable("lan.py",base=base)])