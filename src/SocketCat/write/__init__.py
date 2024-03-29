"""Connect to a socket and read+write data with it. sends stdin to the socket and recvs the socket to stdout"""

import os
import sys
import socket
import select

from .. import common

class Tool(common.Tool):
    @classmethod
    def handler(cls, sock: socket.socket) -> None:
        eof_stdin: bool = False
        eof_sock: bool = False

        fd_stdin = sys.stdin.buffer.fileno()
        fd_sock = sock.fileno()

        poller = select.poll()
        poller.register(fd_stdin, select.POLLIN)
        poller.register(fd_sock, select.POLLIN)

        while any([not eof_stdin, not eof_sock]):
            for fd, revents in poller.poll():
                if fd == fd_stdin:
                    if revents & select.POLLERR:
                        print("poll(): POLLERR from stdin, exiting", file = sys.stderr)
                        raise SystemExit(1)

                    if read := os.read(sys.stdin.buffer.fileno(), 4096):
                        common.writeall(fd_sock, read)
                    else:
                        print("read(): 0 from stdin, calling shutdown(SHUT_WR)", file = sys.stderr)
                        eof_stdin = True
                        poller.unregister(fd_stdin)
                        sock.shutdown(socket.SHUT_WR)

                elif fd == fd_sock:
                    if revents & select.POLLERR:
                        print("poll(): POLLERR from socket, exiting", file = sys.stderr)
                        raise SystemExit(1)

                    recved = os.read(fd_sock, 4096)

                    if recved:
                        common.writeall(sys.stdout.buffer.fileno(), recved)
                    else:
                        print("recv(): 0 from socket; remote end called shutdown(SHUT_WR)", file = sys.stderr)
                        eof_sock = True
                        poller.unregister(fd_sock)
