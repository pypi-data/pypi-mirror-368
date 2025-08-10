import sys
import winreg


def register_protocol(name, script, icon=None):
    ...
    try:
        python_exe = sys.executable

        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, name) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, f"URL:{name} Protocol")
            ...
    except:
        ...
