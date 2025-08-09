#!/home/twinkle/venv/bin/python

######################################################################
# LIBS

from twlog.Code import *

#####################################################################
# CODE

class Filter():
    def __init__(self, name=None) -> None:
        super(Filter, self).__init__()
        self.name = str(name) if name is not None else __name__
    def filter(self, record):
        # Do Nothing
        return True

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["Filter"]

""" __DATA__

__END__ """
