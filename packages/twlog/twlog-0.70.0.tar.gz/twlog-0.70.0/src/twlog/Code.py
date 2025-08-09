#!/home/twinkle/venv/bin/python

import sys

######################################################################
# VARS

LOG_LEVEL = {
    "NOTSET":    0,
    "DEBUG":    10,
    "INFO":     20,
    "WARN":     30,
    "WARNING":  30,
    "ERROR":    40,
    "CRITICAL": 50,
    "NOTICE":   60,
    "ISSUE":    70,
    "MATTER":   80,
}

LEVEL_LOG = {
     0: "NOTSET",
    10: "DEBUG",
    20: "INFO",
    30: "WARN",
    40: "ERROR",
    50: "CRITICAL",
    60: "NOTICE",
    70: "ISSUE",
    80: "MATTER",
}

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

######################################################################
# Module Functions

def addCode(level:int=89, code="NULL"):
    if level < 90 or code is None or code in LOG_LEVEL or code in __dict__:
        return False
    else:
        LOG_LEVEL[code] = level
        LEVEL_LOG[level] = code
        __dict__[code] = level
        return True

def removeCode(level:int=89, code="NULL"):
    if level < 90 or code is None or code not in LOG_LEVEL or code not in __dict__:
        return False
    else:
        LOG_LEVEL.pop([code])
        LEVEL_LOG.pop([level])
        __dict__.pop([code])
        return True

######################################################################
# Module Functions

def _get_caller_class_name():
    import inspect
    caller_frame = inspect.currentframe().f_back
    caller_class = caller_frame.f_locals.get('self', None).__class__
    return caller_class.__name__

def safedate(src: dict, dest: dict):
    for key in dest.keys():
        if key not in src:
            src[key] = dest[key]

def export_global_loglevel(name=None):
    if name is not None:
        c = sys.modules.get(name)
        if c is None:
            c = sys.modules.get(_get_caller_class_name())
            if c is not None:
                # Update
                safedate(src=c.__dict__, dest=LOG_LEVEL)

def export_builtins_loglevel():
    # Update
    safedate(src=__builtins__, dest=LOG_LEVEL)

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["export_global_loglevel", "export_builtins_loglevel", "LOG_LEVEL", "LEVEL_LOG", "NOTSET", "DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL", "NOTICE", "ISSUE", "MATTER"]

""" __DATA__

__END__ """
