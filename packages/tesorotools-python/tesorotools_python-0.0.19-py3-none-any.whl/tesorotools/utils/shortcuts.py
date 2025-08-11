import platform
from pathlib import Path

import win32com.client
from win32com.client import CDispatch


def resolve_shortcut(shortcut: Path) -> Path:
    """Returns the real path behind a shortcut

    Parameters
    ----------
    shortcut : Path
        Path of the shortcut

    Returns
    -------
    Path
        Real path behind the shortcut
    """
    system: str = platform.system()
    if system == "Linux":
        # In linux this is straightforward
        return shortcut
    elif system == "Windows":
        # Little workaround with windows
        shell: CDispatch = win32com.client.Dispatch("WScript.Shell")
        return Path(shell.CreateShortCut(str(shortcut)).Targetpath)
    else:
        # Just return the same if we don't know the OS
        return shortcut
