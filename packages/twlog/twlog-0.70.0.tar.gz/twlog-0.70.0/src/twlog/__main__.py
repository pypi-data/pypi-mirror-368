#!/home/twinkle/venv/bin/python

import os
import sys

from importlib.util import find_spec

######################################################################
# LIBS

from rich.logging import RichHandler

import twlog
import twlog.util

from twlog import *
from twlog.Code import *

######################################################################
# VARS of Namespaced Configurations and DEFS

# __main__.__package__
__package__ = 'twlog'
# __package__.__class__
__twana__ = sys.modules['twlog']
# __spec__
__spec__ = find_spec(__package__)
# __main__.__path__
if __spec__ is not None:
    __root__ = __spec__.submodule_search_locations[0]
    __root__ = os.path.dirname(__root__)
    __root__ = os.path.dirname(__root__)

# Root Path
def get_root_path(path: str = None) -> str:
    """
    指定したパッケージ内のファイルパスを取得するユーティリティ関数。
    Args:
        path (str): 対象ファイル名。
    Returns:
        str: 読み込み可能な一時パス
    """
    return os.path.join(__root__, path)

######################################################################
# MAIN
if __name__ == "__main__":

    # Define True Logger
    #twlog.util.Code.export_global_loglevel(__name__)
    logger = twlog.getLogger(__name__)

    logger.test()

    priny("priny", "priny")
    pixie("pixie", "pixie")
    prain("prain", "prain")
    paint("paint", "paint")
    plume("plume", "plume")
    prank("prank", "prank")
    prown("prown", "prown")
    pinok("pinok", "pinok")
    peach("peach", "peach")
    prism("prism", "prism")

    logger.info('This is test of change title', title='TEST')

    print("")

    # rich
    bconf = twlog.basicConfig(
        level    = twlog.NOTSET,
        format   = "%(message)s",
        datefmt  = "[%X]",
        handlers = [RichHandler(markup=True, rich_tracebacks=True)]
    )
    richlog = twlog.getLogger("rich", handlers = [RichHandler(rich_tracebacks=True)])
    richlog.info("This is test of rich")
    richlog.test()

    print("")

    # stream
    sconf = twlog.basicConfig(
        level    = twlog.NOTSET,
        format   = "%(message)s",
        datefmt  = "[%X]",
        handlers = [StreamHandler()]
    )
    streamlog = twlog.getLogger("stream", handlers = [StreamHandler()])
    streamlog.handlers[0].setFormatter(sconf["formatter"])
    streamlog.info("This is test of StreamHandler")
    streamlog.test()
    streamlog.setLevel(0)

    print("")

    # FileHandler
    filelog = twlog.getLogger("file", handlers = [FileHandler(level=20, filename='sys.stdout', mode='a', encoding=None, delay=True, errors=None)])
    filelog.handlers[0].setFormatter(sconf["formatter"])
    filelog.info("This is test of FileHandler(Output:sys.stdout)")
    filelog.test()
    filelog.setLevel(0)

    print("")

    # BufferedFileHandler
    filelog = twlog.getLogger("file", handlers = [BufferedFileHandler(level=20, filename='sys.stdout', mode='a', encoding=None, delay=True, errors=None)])
    filelog.handlers[0].setFormatter(sconf["formatter"])
    filelog.info("This is test of BufferedFileHandler(Output:sys.stdout)")
    filelog.test()
    filelog.setLevel(0)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = [""]

""" __DATA__

__END__ """
