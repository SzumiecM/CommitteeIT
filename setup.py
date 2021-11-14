from cx_Freeze import setup, Executable

base = None

executables = [Executable("gui.py", base=base)]

packages = ["idna", "tkinter", "matplotlib", "os"]
options = {
    'build_exe': {
        'packages': packages,
    },
}

setup(
    name="<any name>",
    options=options,
    version="<any number>",
    description='<any description>',
    executables=executables
)
