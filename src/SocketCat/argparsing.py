from typing import *
import socket
import socketserver
import argparse
from pathlib import Path

from . import common

def add_socket_address_subparsers(parser: argparse.ArgumentParser):
    parser_address_family = parser.add_subparsers(title = "address", dest = "address_family", required = True,
        description = "which address family (AF) to create the socket in"
    )

    parser_address_family_unix = parser_address_family.add_parser("unix", help = "AF_UNIX")
    parser_address_family_unix.add_argument("address_family_unix_path",
        metavar = "SOCKET-PATH",
        help = "path to Unix socket",
        type = Path
    )

    parser_address_family_inet = parser_address_family.add_parser("inet", help = "AF_INET")
    parser_address_family_inet.add_argument("address_family_inet_ip",
        metavar = "IP",
        help = "IP address"
    )
    parser_address_family_inet.add_argument("address_family_inet_port",
        metavar = "PORT",
        help = "port number",
        type = int
    )

def octal(s: str):
    """Used instead of a lambda for argparse 'invalid octal value' message"""
    return int(s, 8)

def add_server_arguments(parser: argparse.ArgumentParser):
    parser.add_argument("--fork", "-f",
        help = "Have the server call os.fork() after calling socket.listen()",
        action = "store_true"
    )

    parser_address_family = parser.add_subparsers(title = "address", dest = "address_family", required = True,
        description = "which address family (AF) to create the socket in"
    )

    parser_address_family_unix = parser_address_family.add_parser("unix", help = "AF_UNIX")
    parser_address_family_unix.add_argument("address_family_unix_path",
        metavar = "SOCKET-PATH",
        help = "path to Unix socket",
        type = Path
    )
    parser_address_family_unix.add_argument("--chmod",
        metavar = "MODE",
        dest = "address_family_unix_chmod",
        help = "Call os.umask(0o777) before calling socket.bind(), restore umask, and call os.chmod(MODE) on the socket. MODE is in octal, eg --chmod 777 for a public socket",
        type = octal
    )

    parser_address_family_inet = parser_address_family.add_parser("inet", help = "AF_INET")
    parser_address_family_inet.add_argument("address_family_inet_ip",
        metavar = "IP",
        help = "IP address"
    )
    parser_address_family_inet.add_argument("address_family_inet_port",
        metavar = "PORT",
        help = "port number",
        type = int
    )

_af_str_to_af_const = {
    "unix": socket.AF_UNIX,
    "inet": socket.AF_INET,
}

def af_const_from_args(args: argparse.Namespace):
    af: str = getattr(args, "address_family")

    return _af_str_to_af_const[af]

def _socket_address_from_args_unix(args: argparse.Namespace):
    socket_path: Path = getattr(args, "address_family_unix_path")

    return f"{socket_path}"

def _socket_address_from_args_inet(args: argparse.Namespace):
    socket_ip: str = getattr(args, "address_family_inet_ip")
    socket_port: int = getattr(args, "address_family_inet_port")

    return (socket_ip, socket_port)

_af_str_to_address_factory = {
    "unix": _socket_address_from_args_unix,
    "inet": _socket_address_from_args_inet,
}

def socket_address_from_args(args: argparse.Namespace):
    af: str = getattr(args, "address_family")

    return _af_str_to_address_factory[af](args)

_af_str_to_socketserver_class = {
    "unix": common.ForkingUnixStreamServer,
    "inet": socketserver.ForkingTCPServer,
}

def socketserver_class_from_args(args: argparse.Namespace) -> socketserver.BaseServer:
    af: str = getattr(args, "address_family")

    return _af_str_to_socketserver_class[af]
