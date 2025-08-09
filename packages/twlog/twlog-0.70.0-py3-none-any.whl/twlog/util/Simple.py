#!/home/twinkle/venv/bin/python

import os
import sys

import shutil
import inspect

from datetime import datetime

######################################################################
# VARS

# Level
NOTSET   = 0
DEBUG    = 10
INFO     = 20
WARN     = 30
WARNING  = 30
ERROR    = 40
CRITICAL = 50
NOTICE   = 60
ISSUE    = 70
MATTER   = 80

# config
ansi_rich = True
# start (0x1b), reset
ansi_start = "\x1b["
ansi_reset = "\x1b[0m"
# foreground color
ansi_fore_black  = "30"
ansi_fore_red    = "31"
ansi_fore_green  = "32"
ansi_fore_yellow = "33"
ansi_fore_blue   = "34"
ansi_fore_purple = "35"
ansi_fore_cyan   = "36"
ansi_fore_white  = "37"
# foreground light color
ansi_fore_light_gray    = "90"
ansi_fore_light_red     = "91"
ansi_fore_light_green   = "92"
ansi_fore_light_yellow  = "93"
ansi_fore_light_blue    = "94"
ansi_fore_light_magenta = "95"
ansi_fore_light_cyan    = "96"
ansi_fore_light_white   = "97"
# background color
ansi_back_black  = "40"
ansi_back_red    = "41"
ansi_back_green  = "42"
ansi_back_yellow = "43"
ansi_back_blue   = "44"
ansi_back_purple = "45"
ansi_back_cyan   = "46"
ansi_back_white  = "47"
# background light color
ansi_back_light_gray    = "100"
ansi_back_light_red     = "101"
ansi_back_light_green   = "102"
ansi_back_light_yellow  = "103"
ansi_back_light_blue    = "104"
ansi_back_light_magenta = "105"
ansi_back_light_cyan    = "106"
ansi_back_light_white   = "107"
# bold, italic, underline, blink, invert
ansi_text_on_bold       = "1"
ansi_text_off_bold      = "22"
ansi_text_on_italic     = "3"
ansi_text_off_italic    = "23"
ansi_text_on_underline  = "4"
ansi_text_off_underline = "24"
ansi_text_on_blink      = "5"
ansi_text_off_blink     = "25"
ansi_text_on_reverse    = "7"
ansi_text_off_r4everse  = "27"

######################################################################
# DEFS

# fakeLogger
def logger(message: str = None, level: int = INFO, title: str = None):
    if level == DEBUG:
        title = title if title is not None else 'WARN'
        datefmt = f"{ansi_start}{ansi_fore_white};{ansi_text_on_bold}m"
        textfmt = f"{ansi_start}{ansi_back_light_gray};{ansi_fore_white};{ansi_text_on_bold}m"
    elif level == WARN:
        title = title if title is not None else 'WARN'
        datefmt = f"{ansi_start}{ansi_fore_light_yellow};{ansi_text_on_bold}m"
        textfmt = f"{ansi_start}{ansi_back_yellow};{ansi_fore_white};{ansi_text_on_bold}m"
    elif level == ERROR:
        title = title if title is not None else 'ERROR'
        datefmt = "{ansi_start}{ansi_fore_light_red};{ansi_text_on_bold}m"
        textfmt = f"{ansi_start}{ansi_back_red};{ansi_fore_white};{ansi_text_on_bold}m"
    elif level == CRITICAL:
        title = title if title is not None else 'CRITICAL'
        datefmt = f"{ansi_start}{ansi_fore_red};{ansi_text_on_bold}m"
        textfmt = f"{ansi_start}{ansi_back_light_red};{ansi_fore_black};{ansi_text_on_bold}m"
    elif level == NOTICE:
        title = title if title is not None else 'NOTICE'
        datefmt = f"{ansi_start}{ansi_fore_light_green};{ansi_text_on_bold}m"
        textfmt = f"{ansi_start}{ansi_back_green};{ansi_fore_white};{ansi_text_on_bold}m"
    elif level == ISSUE:
        title = title if title is not None else 'ISSUE'
        datefmt = f"{ansi_start}{ansi_fore_light_magenta};{ansi_text_on_bold}m"
        textfmt = f"{ansi_start}{ansi_back_purple};{ansi_fore_white};{ansi_text_on_bold}m"
    elif level == MATTER:
        title = title if title is not None else '\x27O\x27 MATTER'
        datefmt = f"{ansi_start}{ansi_fore_white};{ansi_text_on_bold}m"
        textfmt = f"{ansi_start}{ansi_back_light_white};{ansi_fore_black};{ansi_text_on_bold}m"
    else:
        title = title if title is not None else 'INFO'
        datefmt = f"{ansi_start}{ansi_fore_cyan};{ansi_text_on_bold}m"
        textfmt = f"{ansi_start}{ansi_back_blue};{ansi_fore_white};{ansi_text_on_bold}m"
    # datetime
    dt = datetime.now()
    ds = dt.strftime("[%Y-%m-%d %H:%M:%S]")
    # torch.Tensor
    message = str(message) if isinstance(message, torch.Tensor) is False else ( str(message.item()) if len(message) == 1 else str(message.tolist()) )
    # Rich??
    if ansi_rich is True:
        # initialize
        mf = f"{datefmt}{ds}{ansi_reset} {textfmt}{title}{ansi_reset} {message}"
        ml = 2 + len(ds) + len(title) + len(message) # + X # if wants SP
    else:
        # initialize
        mf = f"{ds} |{title}| {message}"
        ml = len(mf)
    # filename and lineno
    if level >=30:
        fn = os.path.basename(str(inspect.stack()[1].filename))
        ln = str(inspect.stack()[1].lineno)
        if not fn.endswith(".py"):
            fn += ".py"
        fl = f" ({fn}:{ln})"
        ml += len(fl)
        ts = shutil.get_terminal_size().columns
        df = ts - ml
        if df > 0: mf += (" " * df)
        mf += fl
        print(mf, file=sys.stderr)
    # ^^;
    else:
        print(mf, file=sys.stdout)

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["logger", "NOTSET", "DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL", "NOTICE", "MATTER"]

""" __DATA__

__END__ """
