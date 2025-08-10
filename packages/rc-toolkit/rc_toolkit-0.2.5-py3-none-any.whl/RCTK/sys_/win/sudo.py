import sys
import ctypes


def sudo():
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1
        )
        sys.exit()
