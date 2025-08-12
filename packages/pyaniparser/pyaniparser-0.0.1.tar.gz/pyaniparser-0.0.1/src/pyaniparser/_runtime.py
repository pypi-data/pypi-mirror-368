import sys
import threading
from pathlib import Path

_loaded = False
_lock = threading.Lock()


def ensure_loaded() :
    global _loaded
    if _loaded :
        return
    with _lock :
        if _loaded :
            return
        pkg = Path(__file__).resolve().parent
        rc = pkg / "dotnet.runtimeconfig.json"
        lib = pkg / "lib"
        if not rc.exists() : raise FileNotFoundError(rc)
        if not lib.exists() : raise FileNotFoundError(lib)

        import pythonnet
        pythonnet.load("coreclr", runtime_config = str(rc))

        import clr  # noqa
        sys.path.append(str(lib))
        import clr as _clr
        try :
            _clr.AddReference("Banned.AniParser")
        except Exception :
            _clr.AddReference(str(lib / "Banned.AniParser.dll"))
        _loaded = True
