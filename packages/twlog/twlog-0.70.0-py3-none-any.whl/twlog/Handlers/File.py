#!/home/twinkle/venv/bin/python

import os
import sys

import shutil

import locale

######################################################################
# LIBS

from twlog.Code import *
from twlog.Handlers import Handler

######################################################################
# Classes - handlers

class FileHandler(Handler):
    # Initialization
    def __init__(self, level=INFO, filename=None, mode='a', encoding=None, delay=True, errors=None) -> None:
        super(FileHandler, self).__init__(level=level)
        self.level = level if level is not None and level in LOG_LEVEL else DEBUG
        self.filename = str(filename) if filename is not None else 'sys.stdout'
        self.mode = str(mode) if mode is not None else 'a'
        self.encoding = str(encoding) if encoding is not None else locale.getpreferredencoding()
        self.delay = bool(delay) if delay is not None else False
        self.errors = str(errors) if errors is not None else None
        if self.filename == 'sys.stdout':
            self.f = sys.stdout
        elif self.filename == 'sys.stderr':
            self.f = sys.stderr
        elif self.delay is False:
            self.f = open(self.filename, mode=self.mode, encoding=self.encoding, buffering=self.delay, errors=self.errors)
        else:
            self.f = None
    def emit(self, record):
        if record.level < self.level: return
        # Format
        record = self.format(record)
        # ^^;
        if (self.filename != 'sys.stdout' and self.filename != 'sys.stderr') and (self.f is None or self.delay is True):
            with open(self.filename, mode=self.mode, encoding=self.encoding, buffering=self.delay, errors=self.errors) as self.f:
                print(record.message, file=self.f)
        # ^^;
        else:
            print(record.message, file=self.f)
    def flush(self):
        if delay is False:
            self.f.flush()
    def close(self):
        if (self.filename != 'sys.stdout' and self.filename != 'sys.stderr') and self.f is None:
            close(self.f)

class BufferedFileHandler(Handler):
    # Initialization
    def __init__(self, level=INFO, filename=None, mode='a', encoding=None, delay=True, errors=None) -> None:
        super(BufferedFileHandler, self).__init__(level=level)
        self.level = level if level is not None and level in LOG_LEVEL else DEBUG
        self.filename = str(filename) if filename is not None else 'sys.stdout'
        self.mode = str(mode) if mode is not None else 'a'
        self.encoding = str(encoding) if encoding is not None else locale.getpreferredencoding()
        self.delay = bool(delay) if delay is not None else False
        self.errors = str(errors) if errors is not None else None
        # __builtins__.open
        self._open = open
        self._prnt = print
        self._stdo = sys.stdout
        self._stde = sys.stderr
        # Binder
        self.binder = []
        # Stdout?
        if self.filename == 'sys.stdout':
            self.f = self._stdo
        elif self.filename == 'sys.stderr':
            self.f = self._stde
        else:
            self.f = None
    def getBinder(self):
        return self.binder.copy()
    def emit(self, record):
        if record.level < self.level: return
        # Format
        record = self.format(record)
        # ^^;
        self.binder.append(record.message + "\n")
    def flush(self):
        if (self.filename != 'sys.stdout' and self.filename != 'sys.stderr') and self.f is None:
            with self._open(self.filename, mode=self.mode, encoding=self.encoding, buffering=self.delay, errors=self.errors) as self.f:
                for i in self.binder: print(self.binder[i], file=self.f)
        else:
            for i in self.binder: print(i[0:-2], file=self.f)
        self.binder.clear()
    def __del__(self):
        self.flush()

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["FileHandler", "BufferedFileHandler"]

""" __DATA__

__END__ """
