#!/home/twinkle/venv/bin/python

import socket

######################################################################
# LIBS

######################################################################
# VARS

######################################################################
# Classes

######################################################################
# DEFS

# ChatGPT
def run_logger_udp_server(host="0.0.0.0", port=514):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"[Logger UDP Server] Listening on {host}:{port}...")
    try:
        while True:
            data, addr = sock.recvfrom(4096)
            print(f"[{addr}] {data.decode('utf-8').strip()}")
    except KeyboardInterrupt:
        print("Shutting down.")
    finally:
        sock.close()

# ChatGPT
def run_logger_tcp_server(host="0.0.0.0", port=1514):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"[Logger TCP Server] Listening on {host}:{port}...")
    try:
        while True:
            client, addr = server.accept()
            with client:
                print(f"[Connected] {addr}")
                while True:
                    data = client.recv(1024)
                    if not data:
                        break
                    print(f"[{addr}] {data.decode('utf-8').strip()}")
    except KeyboardInterrupt:
        print("Shutting down.")
    finally:
        server.close()

######################################################################
# CODE

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = []

""" __DATA__

__END__ """
