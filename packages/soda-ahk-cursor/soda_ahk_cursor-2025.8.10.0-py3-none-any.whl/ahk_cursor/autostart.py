from win32com.client import Dispatch
from pathlib import Path
import sys

home_folder = Path.home()
python_path = Path(sys.executable).resolve().parent
start_folder = home_folder.joinpath(
    r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
)


def create(path: Path):
    shell = Dispatch("WScript.Shell")
    lnk_file = start_folder.joinpath(path.stem + " - Shortcut.lnk")
    shortcut = shell.CreateShortCut(str(lnk_file))
    shortcut.Targetpath = str(path)
    shortcut.Arguments = ""
    shortcut.WorkingDirectory = str(path.parent)
    shortcut.save()
    return lnk_file
