"""
    Module for storing SSH related stuff
"""
import logging
from typing import Dict
from paramiko import RSAKey, Ed25519Key, SSHException
from sshtunnel import SSHTunnelForwarder
from io import StringIO
from sys import stdout

from .errors import IncorrectParamError


def get_stdout_only_logger():
    logger = logging.getLogger("STDOUTONLY")
    stream_handler = logging.StreamHandler(stream=stdout)
    logger.addHandler(stream_handler)
    return logger


class SSHTunnel:
    """
        General SSH tunnel class-component
        for working with ssh in python Data Sources.

        Arguments:

            host (str):

                Host where resource(database in most cases) is located.
                Example:
                    default host will be: 127.0.0.1

            port (int):

                Port of resource you want to connect to.
                Example:
                    default port for `mongo` will be: 27017

            ssh_tunnel (dictionary):

                General UI object with all required
                information for connecting through ssh tunnel.

                Structure:

                    active (bool):
                        Defines if we will use ssh tunnel for connecting.
                        if True -> using.
                        if False (by default) -> ignoring.

                    port (int):
                        SSH port, by default = 22.

                    host (str):
                        SSH host of remote server.

                    username (str):
                        Name of SSH user.

                    password (str):
                        Password for remote SSH server.
                        Empty by default.

                    privateKey (str):
                        String representation of private key
                        for connecting to ssh server.

                        * Here should not be any newline characters


            platform_ssh (bool, True by default):

                Flag that you can find in source object.
                if False -> we will use python SSHTunnel logic.
                if True -> we will use platform SSH.

        How to Use:

            1) tunnel = SSHTunnel('127.0.0.1', 27017, {...params}, False)
               server = tunnel.server
               ... your code
               server.stop() - important, don't forget to close the socket

            2) with SSHTunnel('127.0.0.1', 27017, {..params}, False) as server:
                   ... your code here - tunnel will be closed automatically

    """
    def __init__(self, host: str, port: int,
                 ssh_tunnel: Dict, platform_ssh: bool = True):
        self.host = host
        self.port = port
        self.tunnel = ssh_tunnel
        self._server = self._get_server(platform_ssh)

    @property
    def server(self):
        return self._server

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        if not isinstance(value, int):
            raise IncorrectParamError("Port should be instance of `int`")
        if value < 0 or value > 65535:
            raise IncorrectParamError("Port should be in range [0: 65535]")

        self._port = value

    @property
    def tunnel(self):
        return self._tunnel

    @tunnel.setter
    def tunnel(self, value):
        if not isinstance(value, dict):
            raise IncorrectParamError("SSH tunnel should be `dict` object")

        required_keys = [
            "active", "host",
            "username", "privateKey"
        ]

        for key in required_keys:
            if not value.get(key):
                msg = f"SSH tunnel object should contain `{key}` property"
                raise IncorrectParamError(msg)

        if not value.get("active", False):
            msg = "To use SSH tunnel connection, property `active` should be `True`"  # noqa
            raise IncorrectParamError(msg)

        value["port"] = int(value.get("port", 22))
        self._tunnel = value

    def _get_server(self, platform_ssh: bool):
        """Method for getting and starting ssh server."""
        if platform_ssh:
            return None

        try:
            pkey = RSAKey.from_private_key(StringIO(self.tunnel["privateKey"]),
                                           password=self.tunnel.get("password"))
        except SSHException:
            pkey = Ed25519Key.from_private_key(StringIO(self.tunnel["privateKey"]),
                                               password=self.tunnel.get("password"))

        server = SSHTunnelForwarder(
            ssh_address_or_host=(self.tunnel["host"], self.tunnel["port"]),
            ssh_username=self.tunnel["username"],
            ssh_password=self.tunnel.get("password"),
            ssh_pkey=pkey,
            remote_bind_address=(self.host, self.port),
            logger=get_stdout_only_logger()
        )
        server.start()

        return server

    def __enter__(self):
        return self._server

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._server:
            self._server.stop()

    def __str__(self):
        return "SSH tunnel to {}, for user {}".format(
            self.tunnel["host"], self.tunnel["username"]
        )
