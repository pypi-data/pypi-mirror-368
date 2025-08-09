#!/home/twinkle/venv/bin/python

import sys

import shutil

######################################################################
# LIBS

from twlog.util.ANSIColor import ansi, ansilen, strlen
from twlog.Code import *
from twlog.Handlers import Handler
from twlog.Formatters import Formatter
from twlog.Formatters.Rich import RichFormatter

######################################################################
# Classes - handlers

class RichHandler(Handler):
    # Initialization
    def __init__(self, level=INFO, stream=sys.stdout, stream_err=sys.stderr, markup=True, rich_tracebacks=True) -> None:
        super(RichHandler, self).__init__(level=level)
        self.level = level if level is not None and level in LOG_LEVEL else DEBUG
        self.stream = stream if stream is not None else sys.stdout
        self.stream_err = stream_err if stream_err is not None else sys.stderr
        self.markup = True if markup is True else False
        self.rich_tracebacks = True if rich_tracebacks is True else False
        self.terminator = '\n'
    def emit(self, record):
        if record.level < self.level: return
        # Format
        record = self.format(record)
        # ^^;
        print(record.message, file=self.stream)
    def flush(self):
        return True
    def setStrteam(self, stream):
        return True

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["RichHandler"]

""" __DATA__

__END__ """
