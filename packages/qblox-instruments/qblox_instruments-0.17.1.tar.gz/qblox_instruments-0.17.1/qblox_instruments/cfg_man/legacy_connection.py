# ----------------------------------------------------------------------------
# Description    : Legacy cfg_man connection adapter class
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

import re
import socket
from collections.abc import Iterable
from typing import BinaryIO, Optional

from qblox_instruments.cfg_man import log
from qblox_instruments.cfg_man.const import VERSION
from qblox_instruments.cfg_man.legacy import (
    exchange_version,
    recv_ack,
    recv_file,
    send_msg,
    send_msg_file,
)
from qblox_instruments.cfg_man.probe import ConnectionInfo

# -- class -------------------------------------------------------------------


class LegacyConnection:
    """
    Connection class for connecting to legacy configuration managers. Do not
    instantiate and use directly; leave this to the ConfigurationManager class
    in main.
    """

    __slots__ = ["_sock"]

    # ------------------------------------------------------------------------
    def __init__(self, ci: ConnectionInfo, timeout: float = 60.0) -> None:
        """
        Opens a legacy configuration manager connection.

        Parameters
        ----------
        ci: ConnectionInfo
            Connection information.
        timeout: float
            Socket timeout.
        """
        super().__init__()
        assert ci.protocol == "legacy"
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(timeout)
        self._sock.connect(ci.address)
        exchange_version(self._sock, VERSION)

    # ------------------------------------------------------------------------
    def close(self) -> None:
        """
        Closes the connection.
        """
        self._sock.close()

    # ------------------------------------------------------------------------
    def set_ip_config(self, config: str) -> None:
        """
        Reconfigures the IP configuration of the device. Changes will only go
        into effect after the device is rebooted.

        Parameters
        ----------
        config: str
            The IP configuration. Must match ``192.168.*.*/24``; other IP
            configurations are not supported by the software running on the
            device.

        Raises
        ------
        NotImplementedError
            For unsupported IP configuration formats.
        """

        # Check configuration and strip prefix length for compatibility.
        if not re.fullmatch("192.168.[0-9]+.[0-9]+/24", config):
            raise NotImplementedError(
                "unsupported IP configuration for the current version of "
                "the software running on the device"
            )
        config = config.split("/")[0]

        send_msg(self._sock, b"ip_addr")
        send_msg(self._sock, config.encode("utf-8"))
        recv_ack(self._sock)

    # ------------------------------------------------------------------------
    def download_log(self, source: str, fmt: int, file: BinaryIO) -> None:
        """
        Downloads log data from the device.

        Parameters
        ----------
        source: str
            The log source. Must be ``"app"``, ``"system"``, or ``"cfg_man"``.
        fmt: int
            Used by the other protocols to specify file format. Must be
            negative here in order to select the tar.gz format, which is the
            only format supported here.
        file: BinaryIO
            Destination file, open in write mode.

        Raises
        ------
        NotImplementedError
            For unsupported values of source or fmt.
        """
        if fmt >= 0:
            raise NotImplementedError(
                "the legacy configuration manager protocol only supports "
                "downloading logs in tgz format"
            )

        if source == "app":
            send_msg(self._sock, b"device_log")
        elif source == "system":
            send_msg(self._sock, b"system_log")
        elif source == "cfg_man":
            send_msg(self._sock, b"cfg_man_log")
        else:
            raise NotImplementedError(f"unknown log source {source}")

        recv_file(self._sock, file)
        recv_ack(self._sock)

    # ------------------------------------------------------------------------
    def update(
        self,
        file: BinaryIO,
        included_slots: Optional[Iterable[int]] = None,
        excluded_slots: Optional[Iterable[int]] = None,
    ) -> None:
        """
        Sends an update package to the device.

        Parameters
        ----------
        file: BinaryIO
            File open in read mode representing the data to be sent.
        included_slots: Optional[Iterable[int]]
            list of included slot indices
        excluded_slots: Optional[Iterable[int]]
            list of excluded slot indices
        """

        if included_slots is not None:
            log.info("Included slots are not supported using the legacy connection")

        if excluded_slots is not None:
            log.info("Excluded slots are not supported using the legacy connection")

        send_msg(self._sock, b"update")
        log.debug("Sending update package...")
        send_msg_file(self._sock, file)
        log.debug("Waiting for device to respond to update request...")
        recv_ack(self._sock)

    # ------------------------------------------------------------------------
    def rollback(self) -> None:
        """
        Sends a rollback request to the device.
        """
        send_msg(self._sock, b"rollback")
        log.debug("Waiting for device to respond to rollback request...")
        recv_ack(self._sock)

    # ------------------------------------------------------------------------
    def reboot(self) -> None:
        """
        Sends a reboot request to the device.
        """
        send_msg(self._sock, b"reboot")
        recv_ack(self._sock)
