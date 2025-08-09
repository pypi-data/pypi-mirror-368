#!/home/twinkle/venv/bin/python

import socket

######################################################################
# LIBS

from twlog.Code import *
from twlog.Handlers import Handler

######################################################################
# Classes - ChatGPT

class SyslogHandler(Handler):
    def __init__(self, address=("localhost", 514), level=INFO):
        super().__init__(level)
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    def emit(self, record):
        record = self.format(record)
        self.socket.sendto(record.message.encode("utf-8"), self.address)

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["SyslogHandler"]

""" __DATA__

__END__ """
