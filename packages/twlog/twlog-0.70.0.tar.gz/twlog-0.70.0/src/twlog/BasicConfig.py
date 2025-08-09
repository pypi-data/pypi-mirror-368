#!/home/twinkle/venv/bin/python

import sys
import threading

######################################################################
# LIBS

from twlog.util.ANSIColor import ansi
from twlog.Code import *
from twlog.Filters import Filter
from twlog.Formatters import Formatter
from twlog.Formatters.ANSI import ANSIFormatter
from twlog.Formatters.Rich import RichFormatter
from twlog.Handlers import Handler
from twlog.Handlers.ANSI import ANSIHandler
from twlog.Handlers.Rich import RichHandler
from twlog.Handlers.File import FileHandler, BufferedFileHandler
from twlog.Handlers.Stream import StreamHandler
from twlog.Handlers.ChatGPT.SysLog import SyslogHandler

######################################################################
# BASIC CONFIG
_basicConfig = {
     "level": INFO,
       "fmt": "%(asctime)s %(levelname)s %(message)s",
   "datefmt": "[%Y-%m-%d %H:%M:%S]",
  "handlers": [],
 "formatter": None,
    "filter": None,
}

######################################################################
# LOCKED CONFIG
_basicConfig_lock = threading.Lock()
_basicConfig_done = False

######################################################################
# DEFS

def basicConfig_lock():
    return _basicConfig_lock
def basicConfig_done():
    return _basicConfig_done
def basicConfig_true():
    _basicConfig_done = True

######################################################################
# CODE

# Filters
_basicConfig["filter"] =  Filter()

# Basic Stream
_basicConfig["formatter"] = Formatter(fmt=_basicConfig["fmt"], datefmt=_basicConfig["datefmt"])
_basicConfig["handlers"] = [StreamHandler(level=INFO, stream=sys.stdout, stream_err=sys.stderr)]
_basicConfig["handlers"][0].setFormatter(_basicConfig["formatter"])
_basicConfig["handlers"][0].addFilter(_basicConfig["filter"])

# ANSI
_basicConfig["formatter_ansi"] = ANSIFormatter(fmt=_basicConfig["fmt"], datefmt=_basicConfig["datefmt"], markup=True, rich_tracebacks=True)
_basicConfig["handlers_ansi"] = [ANSIHandler(level=INFO, stream=sys.stdout, stream_err=sys.stderr, markup=True, rich_tracebacks=True)]
_basicConfig["handlers_ansi"][0].setFormatter(_basicConfig["formatter_ansi"])
_basicConfig["handlers_ansi"][0].addFilter(_basicConfig["filter"])

# Rich
_basicConfig["formatter_rich"] = RichFormatter(fmt=_basicConfig["fmt"], datefmt=_basicConfig["datefmt"], markup=True, rich_tracebacks=True)
_basicConfig["handlers_rich"] = [RichHandler(level=INFO, stream=sys.stdout, stream_err=sys.stderr, markup=True, rich_tracebacks=True)]
_basicConfig["handlers_rich"][0].setFormatter(_basicConfig["formatter_rich"])
_basicConfig["handlers_rich"][0].addFilter(_basicConfig["filter"])

# Basic Configuration
def basicConfig(filename=None, filemode='a', format: str = _basicConfig["fmt"], datefmt: str = "[%Y-%m-%d %H:%M:%S]", style: str = '%', level:int = INFO, stream=None, handlers: list = None, force=False, encoding=None, errors=None):
    _basicConfig["level"] = level if level is not None and level in LOG_LEVEL else INFO
    _basicConfig["fmt"] = str(format) if format is not None and type(format) == 'str' else _basicConfig["fmt"]
    _basicConfig["datefmt"] = str(datefmt) if datefmt is not None and type(datefmt) == 'str' else "[%Y-%m-%d %H:%M:%S]"
    # Handlers
    if handlers is None or len(handlers) == 0:
        if filename is not None:
            _basicConfig["handlers"] = [FileHandler(level=INFO, filename=filename, mode=filemode, encoding=encoding, delay=False, errors=errors)]
            _basicConfig["handlers"][0].setFormatter(_basicConfig["formatter"])
            _basicConfig["handlers"][0].addFilter(_basicConfig["filter"])
        else:
            stream = stream if stream is not None else sys.stdout
            _basicConfig["handlers"] = _basicConfig["handlers_ansi"]
    else:
        _basicConfig["handlers"] = handlers
    # ^^;
    return _basicConfig.copy()

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["basicConfig_lock", "basicConfig_done", "basicConfig_true", "basicConfig"]

""" __DATA__

__END__ """
