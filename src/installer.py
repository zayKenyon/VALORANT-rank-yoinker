import os
import sys
import shutil
import pythoncom
import tkinter
from tkinter import filedialog
from win32com.shell import shell

def install():
    # This prevents an empty tkinter window from appearing
    tkinter.Tk().withdraw()

    print("Select a directory to install vRY to.")

    current_directory = os.getcwd() # Gets the directory from which vRY's exectuable is being run.
    vry_install_path = filedialog.askdirectory(title="Select to a directory to install vRY to") # The directory in which the user chose vRY to be installed in.

    print("Copying files to install directory. Please wait...")

    # Copies all of vRY's files to the user's chosen install directory.
    shutil.copytree(current_directory, vry_install_path, dirs_exist_ok=True)

    print("Creating start menu shortcut...")

    create_start_menu_shortcut(vry_install_path + "/vry.exe", vry_install_path)

    print("Installation complete!")

def create_start_menu_shortcut(vry_exe_path, working_dir):
    shortcut_dir = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
    shortcut_path = shortcut_dir + r"\VALORANT Rank Yoinker.lnk"

    vry_shortcut = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
    persistent_file = vry_shortcut.QueryInterface(pythoncom.IID_IPersistFile)

    vry_shortcut.SetPath(vry_exe_path)
    vry_shortcut.SetWorkingDirectory(working_dir)
    persistent_file.Save(shortcut_path, 0)

