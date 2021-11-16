import sys
from cx_Freeze import setup, Executable

base = None
if (sys.platform == "win32"):
    base = "Win32GUI"

executables = [Executable("CommitteeIT.pyw", base=base)]

packages = ["idna", "tkinter", "matplotlib"]
options = {
    'build_exe': {
        'packages': packages,
    },
}

setup(
    name="CommitteeIT",
    options=options,
    version="1.0",
    description='Committees assembling app.',
    executables=executables
)
