import sys
from cx_Freeze import setup, Executable

import os.path
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

build_exe_options = {
    'packages': ['os', 'tkinter', 'requests', 'pandas', 'time', 'datetime',
                 'ipaddress', 'json', 'threading', 'customFunc', 'numpy',
                 'idna', 'certifi', 'chardet', 'multicolumns', 'logging',
                 'pathlib',],
    'include_files': [
        os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
        os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
        'imgs\prtg_active.ico', 'imgs\PRTG_Logo-Start.ico', 'README.md',
    ],
    'optimize': '2',
}

base = None
if sys.platform == "win32":
  base = "Win32GUI"

setup(
    name='PRTG API Data Access',
    version='0.1.2',
    options={'build_exe': build_exe_options},
    executables=[Executable('PRTG API.py', base=base, shortcutName="PRTG API Access", shortcutDir="DesktopFolder", icon='prtg_active.ico')],
    author='Gerardo Pineda',
    author_email=['gerapv92@gmail.com', 'graupvz@gmail.com']
    description='PRTG API Data Extractor'
)
