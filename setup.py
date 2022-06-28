import sys
from cx_Freeze import setup, Executable
from src.constants import version


build_exe_options = {"path": sys.path}

setup(
    name = "VALORANT rank yoinker",
    version = version,
    description='vRY - Live Match Rank Viewer',
    executables = [Executable("main.py", icon="./assets/Logo.ico", targetName="vry.exe")],
    options={"build_exe": build_exe_options}
)
