#!/home/twinkle/venv/bin/python

import shutil

import inspect
import traceback

from datetime import datetime

######################################################################
# LIBS

from twlog.util.ANSIColor import ansi, ansilen, strlen
from twlog.Code import *
from twlog.Formatters import Formatter

######################################################################
# CLASSES - Formatter

class ANSIFormatter(Formatter):
    def __init__(self, fmt="%(asctime)s %(levelname)s %(message)s", datefmt="[%Y-%m-%d %H:%M:%S]", style='%', validate=True, defaults=None, markup=True, rich_tracebacks=True, *args, **kwargs) -> None:
        super(ANSIFormatter, self).__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate, defaults=defaults, *args, **kwargs)
        self.markup = True if markup is True else False
        self.rich_tracebacks = True if rich_tracebacks is True else False
    def formatLevelName(self, record):
        # MarkUp?
        if self.markup is True:
            if record.level == DEBUG:
                temp = f"{ansi.start}{ansi.back_light_gray};{ansi.fore_white};{ansi.text_on_bold}m"
            elif record.level == WARN:
                temp = f"{ansi.start}{ansi.back_yellow};{ansi.fore_white};{ansi.text_on_bold}m"
            elif record.level == ERROR:
                temp = f"{ansi.start}{ansi.back_red};{ansi.fore_white};{ansi.text_on_bold}m"
            elif record.level == CRITICAL:
                temp = f"{ansi.start}{ansi.back_light_red};{ansi.text_on_bold};{ansi.fore_black}m"
            elif record.level == NOTICE:
                temp = f"{ansi.start}{ansi.back_green};{ansi.fore_white};{ansi.text_on_bold}m"
            elif record.level == ISSUE:
                temp = f"{ansi.start}{ansi.back_purple};{ansi.fore_white};{ansi.text_on_bold}m"
            elif record.level == MATTER:
                temp = f"{ansi.start}{ansi.back_light_white};{ansi.text_on_bold};{ansi.fore_black}m"
            else: # Defaults (INFO)
                temp = f"{ansi.start}{ansi.back_blue};{ansi.fore_white};{ansi.text_on_bold}m"
            spsp = " " * (8 - len(record.levelname))
            record.levelname = f"{temp}" + record.levelname + f"{spsp}{ansi.reset}"
        else:
            record.levelname = f" | {record.levelname} | "
    def formatMessage(self, record):
        # Get Message
        record.message = record.getMessage()
        temp = str(self.fmt)
        rdic = record.__dict__
        rkey = rdic.keys()
        if self.style == '$':
            for key in rkey:
                temp = temp.replace(f"$\x7bkey\x7d", f"{rdic[key]}")
        elif self.style == '{':
            temp = f"{temp}"
        else:
            for key in rkey:
                temp = temp.replace(f"%({key})s", f"{rdic[key]}")
        record.message = temp
        ml = strlen(record.message)
        # filename and lineno
        if record.level >= 30:
            fl = f"({record.filename}:{record.lineno})"
            ml += strlen(fl)
            ts = shutil.get_terminal_size().columns
            df = ts - ml
            if df > 0: record.message += (" " * df)
            record.message += fl
        # exc_info(exc_text)
        if record.exc_text is not None:
            self.formatException(record.exc_info)
            record.message += f"\n{record.exc_text}"
        # sinfo
        if record.stack_info is not None:
            self.formatStack(record.stack_info)
            record.message += f"\n{record.stack_info}"
    # datetime
    def fomatTime(self, record, datefmt=None):
        # DateTime
        dt = datetime.now()
        # MarkUp?
        if self.markup is True:
            # Initialize
            if record.level == DEBUG:
                temp = f"{ansi.start}{ansi.fore_white}m"
            elif record.level == WARN:
                temp = f"{ansi.start}{ansi.fore_light_yellow}m"
            elif record.level == ERROR:
                temp = f"{ansi.start}{ansi.fore_light_red}m"
            elif record.level == CRITICAL:
                temp = f"{ansi.start}{ansi.fore_red}m"
            elif record.level == NOTICE:
                temp = f"{ansi.start}{ansi.fore_light_green}m"
            elif record.level == ISSUE:
                temp = f"{ansi.start}{ansi.fore_light_magenta}m"
            elif record.level == MATTER:
                temp = f"{ansi.start}{ansi.fore_white}m"
            else: # Defaults (INFO)
                temp = f"{ansi.start}{ansi.fore_cyan}m"
            # Colorful DateTime
            record.asctime = f"{temp}" + dt.strftime(datefmt) + f"{ansi.reset}"
        else:
            record.asctime = dt.strftime(datefmt)
        return record.asctime
    def formatException(self, exc_info):
        if not exc_info:
            return ""
        elif self.markup is True:
            return "".join(traceback.format_exception(*exc_info)).strip()
        else:
            return "".traceback.print_exception(*exc_info).strip()
    def formatStack(self, stack_info):
        if not stack_info:
            return ""
        elif self.markup is True:
            return traceback.format_stack(f=stack_info, limit=None)
        else:
            return traceback.print_stack(f=stack_info, limit=None)
    def formatHeader(self, records):
        return records
    def formatFooter(self, records):
        return records
    # Gate
    def format(self, record):
        self.formatLevelName(record)
        # %(asctime)s
        self.fomatTime(record, datefmt=self.datefmt)
        # %(message)s
        self.formatMessage(record)
        # ^^;
        return record

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["ANSIFormatter"]

""" __DATA__

__END__ """
