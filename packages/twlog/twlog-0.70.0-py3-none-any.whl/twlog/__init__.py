#!/home/twinkle/venv/bin/python

import os
import sys
import io
import threading
import re

import time
import locale

import shutil
import inspect
import traceback

import socket

from datetime import datetime

######################################################################
# LIBS

import twlog.util

from twlog.util import psolo, popts, priny, pixie, prain, paint, plume, prank, prown, pinok, peach, prism
from twlog.util.ANSIColor import ansi
from twlog.Code import *
from twlog.BasicConfig import basicConfig, basicConfig_lock, basicConfig_done, basicConfig_true
from twlog.Filters import Filter
from twlog.Formatters import Formatter
from twlog.LogRecord import LogRecord
from twlog.Handlers import Handler
from twlog.Handlers.ANSI import ANSIHandler
from twlog.Handlers.File import FileHandler, BufferedFileHandler
from twlog.Handlers.Stream import StreamHandler

######################################################################
# REGISTRY
_logger_registry = {}

######################################################################
# RootLogger - really fake root logger

class root():
    # Initialization
    def __init__(self, level=DEBUG, propagate=False, parent=None, disabled=False, handlers=[], *args, **kwargs) -> None:
        # Arguments
        self._args = args
        self._kwargs = kwargs
        # Name
        self.name = 'root'
        # Log Level
        self.level = level if level is not None and level in LOG_LEVEL else DEBUG
        # Handlers
        self.handlers = handlers
        # Current
        self.parent = parent if parent is not None else None
        self.propagate = bool(propagate) if propagate is True else False
        self.disabled = bool(disabled) if disabled is True else False
    # Root Fuynctions
    def isEnabledFor(self, level):
        return False if self.disabled is False or self.level < level else True
    def setLevel(self, level):
        self.level = level if level is not None and level in LOG_LEVEL else 10
        for h in range(len(self.handlers)):
            self.handlers[h].setLevel(self.level);
        ch = self.getChildren()
        for n in range(len(ch)):
            if n in _logger_registry:
                ch[n].setLevel(self.level)
        return self.level
    def getEffectiveLevel(self):
        return self.level
    def getChild(self, suffix):
        ret = []
        for key in _logger_registry.keys():
            if key != suffix and re.search(key, suffix):
                ret.append(key)
        return ret
    def getChildren(self):
        ret = []
        for key in _logger_registry.keys():
            if key != self.name and re.search(key, self.name):
                ret.append(key)
        return ret
    def setHandler(self, hdlr):
        self.handlers = hdlr
    def addHandler(self, hdlr):
        self.handlers.append(hdlr)
    def removeHandler(self, hdlr):
        for h in range(len(self.handlers)):
            if hdlr == self.handlers[h]:
                self.handler.pop(h); break
    def hasHandlers(self):
        return True if len(self.handlers) != 0 else False
    def handle(self, record):
        for h in range(len(self.handlers)):
            self.handlers[h].emit(record)
    #========================================
    ## Not yet
    def addFilter(self, *args, **kwargs):
        return True
    def removeFilter(self, *args, **kwargs):
        return True
    def filter(self, record):
        return record
    #========================================
    # Caller Name
    def findCallerName(self):
        caller_frame = inspect.currentframe().f_back
        caller_class = caller_frame.f_locals.get('self', None).__class__
        return caller_class.__name__
    # Caller Module
    def findCallerModule(self):
        caller_frame = inspect.currentframe().f_back
        caller_class = caller_frame.f_locals.get('self', None).__class__
        return caller_class.__module__
    # Caller Stack
    def findCaller(self, stack_info=False, stacklevel=1):
        stack     = inspect.stack()
        sleng     = len(stack)
        #module    = str(stack[1].frame.f_globals.get("__name__", "__main__"))
        funcName  = str(stack[1].frame.f_code.co_name)
        pathname  = str(stack[1].filename)
        #filename  = os.path.basename(self.pathname)
        lineno    = str(stack[1].lineno)
        if not pathname.endswith(".py"):
            pathname += ".py"
        if stack_info is True:
            sinfo = None
            for i in range(sleng):
                p = stack[i].filename
                if p == __file__ or ("importlib" in p and "_bootstrap" in p):
                    stacklevel -= 1
            with io.StringIO() as sio:
                sio.write("Stack (most recent call last):\n")
                traceback.print_stack(stack[(stacklevel+1)].frame, file=sio)
                sinfo = sio.getvalue()
                if sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]
            return (pathname, lineno, funcName, sinfo)
        else:
            return (pathname, lineno, funcName, None)
    def makeRecord(self, name, level, pathname, lineno, msg, exc_info=None, func=None, extra=None, sinfo=None, *args, **kwargs):
        return LogRecord(name=name, level=level, pathname=pathname, lineno=lineno, msg=msg, exc_info=exc_info, func=func, extra=extra, sinfo=sinfo, *args, **kwargs)
    #========================================
    # Override
    def process(self, msg, **kwargs):
        return (msg, kwargs)
    def manager(self):
        return
    #========================================
    ## Not yet
    def addCode(self, level, code, callback=None):
        twilog.Code.addCode(level, code)
    def removeCode(self, level, code, callback=None):
        twilog.Code.addCode(level, code)
    #========================================
    # Array Disaddembly
    def msg_disassembly(self, msg):
        if hasattr(msg, 'tolist'):
            try: msg = str(msg.tolist())
            except: msg = str(msg)
        elif hasattr(msg, 'item'):
            try: msg = str(msg.item())
            except: msg = str(msg)
        else: msg = str(msg)
        return msg
    # Promise for Console
    def _log(self, msg:any = None, level: int = 20, title: str = None, exc_info=False, func=None, extra=None, sinfo=False, *args, **kwargs):
        if level < self.level: return
        # Title Setting
        title = str(title) if title is not None else self.name.upper()
        level = level if level is not None else self.level
        # numpy.ndarray, torch.Tensor, Jax, ...
        msg = msg if isinstance(msg, str) else self.msg_disassembly(msg)
        # stack_info
        (pathname, lineno, funcName, stack_info) = self.findCaller(stack_info=sinfo, stacklevel=1)
        # exc_info
        exc_args = sys.exc_info() if exc_info is True else None
        # to makeRecord
        records = self.makeRecord(title, level, pathname, lineno, msg, exc_info=exc_args, func=funcName, extra=extra, sinfo=stack_info, *args, **kwargs)
        # Handlers
        self.handle(records)
    def test(self, msg: any = None):
        for l in LOG_LEVEL.keys():
            if l == "NOTSET": continue
            self.__call__((msg if msg is not None else l), level=LOG_LEVEL[l], title=l)
    # Logging
    def log(self, msg:any = None, level: int = 20, title: str = None, exc_info=True, func=None, extra=None, sinfo=None, *args, **kwargs):
        title = title if title is not None else 'LOG'
        if self.propagate is True and self.parent is not None:
            self.parent._log(msg=msg, level=level, title=title, exc_info=False, func=None, extra=None, sinfo=None)
        self._log(msg=msg, level=level, title=title, exc_info=exc_info, func=func, extra=extra, sinfo=sinfo, *args, **kwargs)
    # Exception (ERROR)
    def exception(self, msg:any = None, title: str = None, exc_info=True, func=None, extra=None, sinfo=None, *args, **kwargs):
        title = title if title is not None else 'EXCEPT'
        if self.propagate is True and self.parent is not None:
            self.parent._log(msg=msg, level=ERROR, title=title, exc_info=True, func=None, extra=None, sinfo=None, *args, **kwargs)
        self._log(msg=msg, level=ERROR, title=title, exc_info=exc_info, func=func, extra=extra, sinfo=sinfo, *args, **kwargs)
    # Wrappers
    def debug(self, msg:any = None, level=10, title=None, exc_info=True, func=None, extra=None, sinfo=None, *args, **kwargs):
        title = title if title is not None else 'DEBUG'
        self._log(msg=msg, level=level, title=title, exc_info=exc_info, func=func, extra=extra, sinfo=sinfo, *args, **kwargs)
    def info(self, msg:any = None, level=20, title=None, exc_info=False, func=None, extra=None, sinfo=None, *args, **kwargs):
        title = title if title is not None else 'INFO'
        self._log(msg=msg, level=level, title=title, exc_info=exc_info, func=func, extra=extra, sinfo=sinfo, *args, **kwargs)
    def warn(self, msg:any = None, level=30, title=None, exc_info=False, func=None, extra=None, sinfo=None, *args, **kwargs):
        title = title if title is not None else 'WARN'
        self._log(msg=msg, level=level, title=title, exc_info=exc_info, func=func, extra=extra, sinfo=sinfo, *args, **kwargs)
    def error(self, msg:any = None, level=40, title=None, exc_info=False, func=None, extra=None, sinfo=None, *args, **kwargs):
        title = title if title is not None else 'ERROR'
        self._log(msg=msg, level=level, title=title, exc_info=exc_info, func=func, extra=extra, sinfo=sinfo, *args, **kwargs)
    def critical(self, msg:any = None, level=50, title=None, exc_info=False, func=None, extra=None, sinfo=None, *args, **kwargs):
        title = title if title is not None else 'CRITICAL'
        self._log(msg=msg, level=level, title=title, exc_info=exc_info, func=func, extra=extra, sinfo=sinfo, *args, **kwargs)
    def notice(self, msg:any = None, level=60, title=None, exc_info=False, func=None, extra=None, sinfo=None, *args, **kwargs):
        title = title if title is not None else 'NOTICE'
        self._log(msg=msg, level=level, title=title, exc_info=exc_info, func=func, extra=extra, sinfo=sinfo, *args, **kwargs)
    def issue(self, msg:any = None, level=70, title=None, exc_info=False, func=None, extra=None, sinfo=None, *args, **kwargs):
        title = title if title is not None else 'ISSUE'
        self._log(msg=msg, level=level, title=title, exc_info=exc_info, func=func, extra=extra, sinfo=sinfo, *args, **kwargs)
    def matter(self, msg:any = None, level=80, title=None, exc_info=False, func=None, extra=None, sinfo=None, *args, **kwargs):
        title = title if title is not None else '\x27O\x27 MATTER'
        self._log(msg=msg, level=level, title=title, exc_info=exc_info, func=func, extra=extra, sinfo=sinfo, *args, **kwargs)
    #========================================
    def __call__(self, msg:any = None, level=None, title=None, exc_info=False, func=None, extra=None, sinfo=None, *args, **kwargs):
        level = level if level is not None else self.level
        if level == NOTSET: self.log(level, msg, title=title)
        elif level == DEBUG: self.debug(msg, level=level, title=title)
        elif level == WARN: self.warn(msg, level=level, title=title)
        elif level == ERROR: self.error(msg, level=level, title=title)
        elif level == NOTICE: self.notice(msg, level=level, title=title)
        elif level == ISSUE: self.issue(msg, level=level, title=title)
        elif level == MATTER: self.matter(msg, level=level, title=title)
        else: self.info(msg, level=level, title=title)

######################################################################
# Logger
class logging(root, ansi):
    # Initialization
    def __init__(self, name=None, level=INFO, propagate=False, parent=None, disabled=False, handlers=[], *args, **kwargs) -> None:
        super(logging, self).__init__(level=level, propagate=propagate, parent=parent, disabled=False, handlers=handlers, *args, **kwargs)
        self.name = str(name) if name is not None else __name__
        # for Priny {ansi.start}...m
        self.first            = "🌠 \x1b[94;1m"
        # ?{ansi.reset}
        self.title_structure  = ":\x1b[0m"
        # e.g. -> {ansi.start}{ansi.fore_light_red};{ansi.text_on_bold}m->{ansi.reset}
        self.middle_structure = ""
        self.split            = " "
    #========================================
    # Safe Update
    def safedate(self, src: dict, dest: dict) -> dict:
        for key in dest.keys():
            if key not in src:
                src[key] = dest[key]
    # Export Log Level
    def export_global_loglevel(self, name=None):
        if name is not None:
            c = sys.modules.get(name)
            if c is None:
                c = sys.modules.get(_get_caller_class_name())
                if c is not None:
                    # Update
                    safedate(src=c.__dict__, dest=LOG_LEVEL)
    #========================================
    # Print for as options pair values. You guys not yet see EBI 🍤🍤🍤🍤
    def popts(self, b, *t):
        b = str(b)
        a = [""] * len(t) 
        for i in range(len(t)):
            a[i] = str(t[i])
        m = f"\x1b[1m{b}:\x1b[0m "
        m += ", ".join(a)
        print(f"{m}")
    #========================================
    # No All Breaks ∞ Looping
    def psolo(self, *t):
        for i in range(len(t)):
            print(t[i], end='')
    #========================================
    # Priny: 🌠 Free Style 自由形式
    def priny(self, b, *t):
        b = str(b)
        a = [""] * len(t) 
        for i in range(len(t)):
            a[i] = str(t[i])
        m = f"{self.first}{b}{self.title_structure}{self.middle_structure} "
        m += f"{self.split}".join(a)
        print(m)
    #========================================
    # Pixie: 🧚✨✨✨ たのしいデバッグ用
    def pixie(self, b, *t):
        b = str(b)
        a = [""] * len(t) 
        for i in range(len(t)):
            a[i] = str(t[i])
        #m = f"🧚✨✨✨ {ansi.start}{ansi.fore_light_blue};{ansi.text_on_blink};{ansi.text_on_bold}m{b} {ansi.reset}✨✨ "
        m = f"🧚✨✨✨ \x1b[36;5;1m{b}\x1b[0m ✨✨ "
        m += ", ".join(a)
        print(m)
    #========================================
    # Prain: 🌈 Rainbow 🌈
    def prain(self, b, *t):
        b = str(b)
        a = [""] * len(t) 
        for i in range(len(t)):
            a[i] = str(t[i])
        #m = f"{ansi.start}{ansi.fore_light_yellow};{ansi.text_on_bold}m{b}:{ansi.reset} "
        m = f"\x1b[93;1m{b}:\x1b[0m "
        m += ", ".join(a)
        print(f"🌈 {m}")
    #========================================
    # Paint: 🎨 Paint Brush 🖌️
    def paint(self, b, *t):
        b = str(b)
        a = [""] * len(t) 
        for i in range(len(t)):
            a[i] = str(t[i])
        #m = f"{ansi.start}{ansi.fore_light_magenta};{ansi.text_on_bold}m{b}:{ansi.reset} "
        m = f"\x1b[95;1m{b}\x1b[0m 🖌️ "
        m += "\x20🖌️".join(a)
        print(f"🎨 {m}")
    #========================================
    # Plume: 🌬️ふーっ🌬️
    def plume(self, b, *t):
        b = str(b)
        a = [""] * len(t) 
        for i in range(len(t)):
            a[i] = str(t[i])
        #m = f"{ansi.start}{ansi.fore_white};{ansi.text_on_bold}m{b}{ansi.reset} 🌬️\x20\x20"
        m = f"\x1b[97;1m{b}\x1b[0m 🌬️ "
        n = " ".join(a)
        #print(f"{m} {ansi.start}{ansi.fore_light_cyan};{ansi.text_on_italic}m{n}{ansi.reset} ")
        print(f"🌬️\x20\x20{m} \x1b[96;3m{n}\x1b[0m")
    #========================================
    # Prank: 🤡🎭
    def prank(self, b, *t):
        b = str(b)
        a = [""] * len(t) 
        for i in range(len(t)):
            a[i] = str(t[i])
        #m = f"{ansi.start}{ansi.fore_light_green};{ansi.text_on_bold}m{b}{ansi.reset} {ansi.start}{ansi.fore_light_red};{ansi.text_on_bold}m->{ansi.reset} "
        m = f"\x1b[92;1m{b}\x1b[0m \x1b[91;1m->\x1b[0m "
        m += " ".join(a)
        print(f"🤡 {m}")
    #========================================
    # Pinok: 🍄きのこ🍄 🍄‍🟫生えた🍄‍🟫
    def pinok(b, *t):
        b = str(b)
        a = [""] * len(t) 
        for i in range(len(t)):
            a[i] = str(t[i])
        #m = f"{ansi.start}{ansi.fore_light_red};{ansi.text_on_bold}m{b}:{ansi.reset} "
        m = f"\x1b[91;1m{b}:\x1b[0m "
        m += ", ".join(a)
        print(f"🍄 {m}")
    #========================================
    # Peach: 🍑桃さんくださ〜い！
    def peach(b, *t):
        b = str(b)
        a = [""] * len(t) 
        for i in range(len(t)):
            a[i] = str(t[i])
        #m = f"{ansi.start}{ansi.fore_light_red};{ansi.text_on_bold}m{b}:{ansi.reset} "
        m = f"\x1b[95;1m{b}:\x1b[0m "
        m += ", ".join(a)
        print(f"🍑 {m}")
    #========================================
    # Prown: 🦞えび🦞 🍤Fried Prown🍤
    def prown(self, b, *t):
        b = str(b)
        a = [""] * len(t) 
        for i in range(len(t)):
            a[i] = str(t[i])
        #m = f"{ansi.start}{ansi.fore_light_red};{ansi.text_on_bold}m{b}:{ansi.reset} "
        m = f"\x1b[91;1m{b}:\x1b[0m "
        m += ", ".join(a)
        print(f"🍤 {m}")
    #========================================
    # Prism: 三稜鏡 🔮💎🪩🎆🎇🪅🎊🎉🎑☄️✨🌌🌠🌫️🫧🌈🏜️🏞️🌅🌄
    def prism(self, b, *t):
        b = str(b)
        a = [""] * len(t) 
        for i in range(len(t)):
            a[i] = str(t[i])
        #m = f"{ansi.start}{ansi.fore_cyan};{ansi.text_on_bold}m{b}:{ansi.reset}\n\t"
        m = f"\x1b[96;1m{b}:\x1b[0m\n\t"
        m += "\n\t".join(a)
        print(f"🪩 {m}")

######################################################################
# CODE

# ChatGPT
def getLogger(name=None, propagate=False, disabled=False, handlers=[], *args, **kwargs):
    if not name:
        name = "__main__"
    if name in _logger_registry:
        return _logger_registry[name]
    # Get Parent
    parent_name = ".".join(name.split(".")[:-1]) if "." in name else None
    parent = _logger_registry.get(parent_name) if parent_name else None
    # basicConfig
    bconf = basicConfig(handlers=handlers, *args, **kwargs)
    # Logger
    logger = logging(name=name, level=bconf["level"], propagate=False, parent=parent, disabled=False, handlers=bconf["handlers"], *args, **kwargs)
    _logger_registry[name] = logger
    # ^^;
    return logger

######################################################################
# CONFIG COMPATIBILITY FUNCS

def RootLogger(*args, force=False, **kwargs):
    """
    logging.basicConfig 互換
    最初に一度だけ設定し、root を構成します。
    """
    with basicConfig_lock():
        if basicConfig_done() and not force:
            return
        basicConfig(*args, **kwargs)
        rlog = getLogger("__main__")
        basicConfig_true()
        return rlog

######################################################################
# getLogger

root = RootLogger()

######################################################################
# Log Level Compatibility

def debug(*args, **kwargs):
    root.debug(*args, **kwargs)
def info(*args, **kwargs):
    root.info(*args, **kwargs)
def warning(*args, **kwargs):
    root.warning(*args, **kwargs)
def warn(*args, **kwargs):
    root.warn(*args, **kwargs)
def error(*args, **kwargs):
    root.error(*args, **kwargs)
def critical(*args, **kwargs):
    root.critical(*args, **kwargs)
def notice(*args, **kwargs):
    root.notice(*args, **kwargs)
def issue(*args, **kwargs):
    root.issue(*args, **kwargs)
def matter(*args, **kwargs):
    root.matter(*args, **kwargs)
def exception(*args, **kwargs):
    root.exception(*args, **kwargs)

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["getLogger", "logging",
    "debug", "info", "warn", "warning", "error", "critical", "notice", "issue", "matter", "exception",
    "ANSIHandler",  "FileHandler", "BufferedFileHandler", "StreamHandler",
    "psolo", "popts", "priny", "pixie", "prain", "paint", "plume", "prank", "prown", "pinok", "peach", "prism",
    ]

""" __DATA__

__END__ """
