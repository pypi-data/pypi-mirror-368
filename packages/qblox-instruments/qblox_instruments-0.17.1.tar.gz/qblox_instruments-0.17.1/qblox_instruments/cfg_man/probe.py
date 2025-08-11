# ----------------------------------------------------------------------------
# Description    : "Smart" automatic configuration for connecting to a host
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

import socket
import struct
from collections import namedtuple
from typing import Callable, Optional, Union

from qblox_instruments.build import BuildInfo, DeviceInfo
from qblox_instruments.cfg_man import log
from qblox_instruments.cfg_man.const import VERSION
from qblox_instruments.cfg_man.legacy import (
    exchange_version,
    recv_ack,
    recv_msg,
    send_msg,
)
from qblox_instruments.ieee488_2 import IpTransport
from qblox_instruments.pnp import (
    CMM_SLOT_INDEX,
    PNP_PORT,
    AddressInfo,
    PlugAndPlay,
    resolve,
)
from qblox_instruments.scpi import CfgMan

# -- probe_port() ------------------------------------------------------------

# Result of probe_port()
PortInfo = namedtuple("PortInfo", ["protocol", "version", "device"])

PortInfo.__doc__ = """
Protocol information for a particular IP/TCP port pair, supporting the legacy
configuration manager protocol and SCPI.
"""

PortInfo.protocol.__doc__ = """
:str: The type of host we're connected to, which will be one of the following
values.

 - ``"legacy_cfg_man"``: a legacy configuration manager. The
   ``update()`` function from this file can be used to update the
   device, but other features will not work (use an older
   configuration manager if you need them).
 - ``"legacy_app"``: a legacy application without configuration
   management commands.
 - ``"cfg_man"``: the configuration manager application via SCPI.
   This application can manage the device at the given host, but
   only that device.
 - ``"app"``: the instrument application via SCPI. This means the
   connection is fully-featured, including the ability to configure
   modules (if this is a CMM).
"""

PortInfo.version.__doc__ = """
:str: Configuration manager server version.
"""

PortInfo.device.__doc__ = """
:DeviceInfo: Device information structure.
"""


# ----------------------------------------------------------------------------
def probe_port(
    host: str,
    port: int,
    version: tuple[int, int, int],
    timeout: float = 10.0,
    slot: Optional[int] = None,
) -> PortInfo:
    """
    Automatically detects what type of application is listening on the given
    host and port.

    Parameters
    ----------
    host: str
        IP address or hostname of the server to connect to.
    port: int
        Port to connect to.
    version: tuple[int, int, int]
        Our client version.
    timeout: float
        Socket timeout in seconds.
    slot: int, Optional
        Slot number to use for the connection via CMM. If `None`, uses port for
        the connection

    Returns
    -------
    PortInfo
        Information about the protocol.

    Raises
    ------
    ValueError
        If the configuration manager returned something we didn't expect.
    """

    # Set default return values.
    protocol = "unknown"
    device = None
    server_version = (0, 0, 0)

    # Open the connection.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        sock.connect((host, port))

        # Send a dummy version in the old protocol format to get past the
        # version exchange. Note that we always reconnect anyway, so it
        # doesn't matter that this isn't the real version. What does matter
        # is that it consists exclusively of characters illegal in SCPI.
        send_msg(sock, b"\xff\xff\xff")

        # Send a SCPI command encapsulated in the old format. Again, the old
        # format will only send bytes here that SCPI doesn't recognize and
        # ignores with an error.
        send_msg(sock, b"\nSYST:ERR?\n")

        # The old server responds to unknown commands with a disconnection, so
        # it will "respond" to the above sequence with only its version
        # message (which it sends immediately after accepting the connection)
        # followed by a disconnection event. The version message starts with a
        # 0x03, since that's the LSB of the size of the version structure.
        # SCPI on the other hand will respond to the SYST:ERR?, since that's
        # the only thing it recognizes in the stream of garbage we sent. This
        # message always starts with ASCII '-', the sign of the error code.
        r = sock.recv(1)

    if r == b"\x03":
        # Okay, so this is a legacy configuration manager.
        protocol = "legacy_cfg_man"

        # Open a new connection that follows the protocol properly to get
        # version and build information.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))

            # Do a proper handshake this time.
            server_version = exchange_version(sock, version)

            # Query device information.
            send_msg(sock, b"idn")
            manufacturer = recv_msg(sock).decode(encoding="utf-8", errors="replace").strip()
            model = recv_msg(sock).decode(encoding="utf-8", errors="replace").strip()
            build_data = recv_msg(sock)
            recv_ack(sock)

        # Unpack binary build information.
        *version, build, hsh, dirty = struct.unpack("BBBxIII", build_data)
        device = DeviceInfo(
            manufacturer=manufacturer,
            model=model,
            cfg_man_build=BuildInfo(version, build, hsh, bool(dirty)),
        )

    elif r == b"-":
        fall_back_to_idn = False

        try:
            # Attempt to use the `*DESCribe?` SCPI command to obtain detailed
            # device information.
            with IpTransport(host, port, timeout) as transport:
                cm = CfgMan(transport)
                description = cm.get_json_description()

                # If description is empty, set fallback flag
                if not description:
                    fall_back_to_idn = True
                elif "modules" in description and slot is not None and slot != CMM_SLOT_INDEX:
                    description = description["modules"].get(f"{slot}", {})

                # Parse device information from the description if not falling back
                if not fall_back_to_idn:
                    device = DeviceInfo.from_dict(description)
        except Exception:
            # If any error occurs with `*DESCribe?`, fallback to `*IDN?`
            fall_back_to_idn = True

        if fall_back_to_idn:
            with IpTransport(host, port, timeout) as transport:
                cm = CfgMan(transport)
                # Use `*IDN?` to obtain device information.
                idn = cm._get_idn()
                # Parse device information from the IDN response
                device = DeviceInfo.from_idn(idn)

        # Determine which connection type we are based on the existence of the
        # app and cfg_man keys in BuildInfo.
        if "cfg_man" in device:
            server_version = device.cfg_man_build.version
            protocol = "app" if "sw" in device else "cfg_man"
        elif "sw" in device:
            protocol = "legacy_app"
        else:
            raise ValueError("received unexpected response during protocol detection")

    else:
        raise ValueError("received unexpected response during protocol detection")

    return PortInfo(protocol, server_version, device)


# -- probe_device() ----------------------------------------------------------

# Result of probe_device()
ConnectionInfo = namedtuple(
    "ConnectionInfo",
    [
        "identifier",
        "protocol",
        "address",
        "slot_index",
        "ip_config",
        "server_version",
        "client_version",
        "device",
        "all_updatable_models",
    ],
)

ConnectionInfo.__doc__ = """
Configuration manager connection information structure.
"""

ConnectionInfo.identifier.__doc__ = """
:Union[str, AddressInfo]: Device identifier or address, as passed to
:func:`~probe_device()`.
"""

ConnectionInfo.protocol.__doc__ = """
:str: The protocol that must be used to connect. Can be:

 - ``"legacy"`` for the legacy configuration manager protocol;
 - ``"scpi"`` for the SCPI-based configuration manager protocol; or
 - ``"pnp"`` when the device is not accessible due to IP address
   misconfiguration.
"""

ConnectionInfo.address.__doc__ = """
:Union[str, tuple[str, int]]: Two-tuple of the IP address and port we need to
use to connect for legacy and SCPI connections, or the device serial number
for plug & play.
"""

ConnectionInfo.slot_index.__doc__ = """
:Optional[int]: None for entire device, slot index if only a single module in
the device will be affected.
"""

ConnectionInfo.ip_config.__doc__ = """
:str: The IP configuration of the device that will be applied when the device
is rebooted, if known. May or may not match the address field, as the
configuration may have changed since the instrument was last rebooted, and the
local IP address of the instrument may differ from what we're connecting to if
NAT is involved.
"""

ConnectionInfo.server_version.__doc__ = """
:Optional[tuple[int, int, int]]: Configuration manager server version, if
known. Will be None for plug & play.
"""

ConnectionInfo.client_version.__doc__ = """
:tuple[int, int, int]: Configuration manager client version.
"""

ConnectionInfo.device.__doc__ = """
:DeviceInfo: Device information structure.
"""

ConnectionInfo.all_updatable_models.__doc__ = """
:set[str]: Set of lowercase model names that will need to be present in the
update package. Must include ``{device}``, but the cluster management module
may for instance request more model names.
"""


# ----------------------------------------------------------------------------
def represent_address(ci: ConnectionInfo) -> str:
    """
    Returns a human-readable string representation of the address.

    Parameters
    ----------
    ci: ConnectionInfo
        The connection information object to represent the address of.

    Returns
    -------
    str
        String representation of the address.
    """
    if ci.protocol == "pnp":
        address = ci.address
    elif ":" in ci.address[0]:
        address = "[{}]:{}".format(*ci.address)
    else:
        address = "{}:{}".format(*ci.address)
    return address


# ----------------------------------------------------------------------------
def represent_connection(ci: ConnectionInfo) -> str:
    """
    Returns a human-readable string representation of the connection.

    Parameters
    ----------
    ci: ConnectionInfo
        The connection information object to represent the connection of.

    Returns
    -------
    str
        String representation of the connection.
    """
    return "{} using {}".format(
        represent_address(ci),
        {
            "pnp": "Qblox plug & play only (IP & name configuration only)",
            "legacy": "legacy configuration manager (update only)",
            "scpi": "SCPI",
        }.get(ci.protocol, "?"),
    )


# ----------------------------------------------------------------------------
def represent_device(ci: ConnectionInfo) -> str:
    """
    Returns a human-readable string representation of the device we're
    connecting to.

    Parameters
    ----------
    ci: ConnectionInfo
        The connection information object to represent the device of.

    Returns
    -------
    str
        String representation of the device.
    """
    info_parts = []
    if ci.device.serial is not None:
        info_parts.append(f"serial {ci.device.serial}")
    if ci.device.name is not None:
        info_parts.append(f"name {ci.device.name}")
    info = f", with {' and '.join(info_parts)}" if info_parts else ""
    return (
        f"{ci.device} at address {represent_address(ci)} "
        f"({'whole instrument' if ci.slot_index is None else f'only slot {ci.slot_index}'}){info}"
    )


# ----------------------------------------------------------------------------
def pprint_connection_info(ci: ConnectionInfo, output: Callable[[str], None] = log.info) -> None:
    """
    Pretty-prints information about a connection information object.

    Parameters
    ----------
    ci: ConnectionInfo
        The connection information object to pretty-print.
    output: Callable[[str], None]
        The function used for printing. Each call represents a line.
    """

    # Format address.
    if ci.protocol == "pnp":
        address = ci.address
        port = PNP_PORT
    else:
        address, port = ci.address

    # Format protocol.
    protocol = "{}{}".format(
        {
            "pnp": "Qblox plug & play only (IP & name configuration only), via UDP broadcast port ",
            "legacy": "legacy configuration manager (update only), via TCP port ",
            "scpi": "SCPI, via TCP port ",
        }.get(ci.protocol, "?"),
        port,
    )

    # Format scope.
    if ci.slot_index is None:
        scope = "entire instrument"
    elif ci.slot_index == 0:
        scope = "only the cluster management module"
    else:
        scope = f"only the module in slot {ci.slot_index}"

    # Format server version.
    server_version = "n/a" if ci.server_version is None else ".".join(map(str, ci.server_version))

    # Format submodule model names.
    submodule_models = ", ".join(
        (
            ci.all_updatable_models
            if ci.device.modules is None
            else {module.model for module in ci.device.modules.values()}
        )
        - {ci.device.model}
    )
    if not submodule_models:
        submodule_models = "n/a"

    # Print connection information.
    output(f"Connecting to            : {address}")
    output(f"Via protocol             : {protocol}")
    output(f"Configuration scope      : {scope}")
    output(f"Server version           : {server_version}")
    output(f"Client version           : {'.'.join(map(str, ci.client_version))}")
    output("-------------------------:-------------------------")
    output(f"Device type              : {ci.device}")
    output(f"Device name              : {ci.device.name}")
    output(f"Serial number            : {ci.device.serial}")
    output(f"IP configuration         : {ci.ip_config}")
    output(f"Submodule types          : {submodule_models}")
    for key, pretty in (
        ("sw", "Application"),
        ("fw", "FPGA firmware"),
        ("kmod", "Kernel module"),
        ("cfg_man", "Config. manager"),
    ):
        if key in ci.device:
            output(f"{pretty + ' version':<25}: {ci.device[key]}")


# ----------------------------------------------------------------------------
def connection_info_to_json(ci: ConnectionInfo) -> dict:
    """
    Converts a ConnectionInfo object to a JSON-serializable representation
    thereof.

    Parameters
    ----------
    ci: ConnectionInfo
        The connection information object to pretty-print.

    Returns
    -------
    dict
        A structure using only JSON-serializable types with all the information
        of the ConnectionInfo object in it.
    """
    d = ci._asdict()
    d["device"] = d["device"].to_dict()
    d["all_updatable_models"] = list(d["all_updatable_models"])
    return d


# ----------------------------------------------------------------------------
def probe_device(
    identifier: Union[str, AddressInfo, ConnectionInfo], quiet: bool = False
) -> ConnectionInfo:
    """
    Automatically detects how to manage the given device.

    Parameters
    ----------
    identifier: str
        Instrument identifier. See :func:`~qblox_instruments.resolve()` for
        more information.
    quiet: bool
        When set, don't log anything.

    Returns
    -------
    ConnectionInfo
        The detected connection and device information.

    Raises
    ------
    RuntimeError
        if we failed to connect.
    """

    # Fallthrough if input is already a resolved configuration structure.
    if isinstance(identifier, ConnectionInfo):
        return identifier

    # Figure out our client version, taken from the generated SCPI class.
    client_version = VERSION

    # Figure out how to connect to the device with the given identifier.
    info = resolve(identifier)
    protocol = info.protocol
    address = info.address
    slot_index = info.slot_index
    app_port = info.scpi_port
    cfg_port = info.cfg_port

    # Load default return values.
    full_address = address
    ip_config = "unknown"
    server_version = None
    device = None
    all_updatable_models = set()
    fall_back_to_cmm = False

    # Handle the case where we can only connect via plug & play.
    if protocol == "pnp":
        # Get device information via plug & play.
        with PlugAndPlay() as p:
            description = p.describe(identifier).get("description", {})

        # Parse build information.
        device = DeviceInfo.from_dict(description)
        all_updatable_models.add(device.model)

    elif protocol == "ip":
        # Preferentially connect to the application.
        fall_back_to_cfg_man = False
        fall_back_to_cmm = False

        # Try to connect to the application running on the device with a
        # short timeout (since it's acceptable if we can't connect to it).
        if not quiet:
            log.info("Trying to connect to application (port %d)...", app_port)
        info = None
        try:
            info = probe_port(address, app_port, client_version, 1.0)
        except Exception as e:
            fall_back_to_cfg_man = True
            if not quiet:
                log.info(
                    "Failed to connect to application (%s), falling back to cfg_man.",
                    e,
                )
        if info is not None:
            # We can connect to the application. Update device information
            # from what we've learned from this.
            protocol = "scpi"
            full_address = (address, app_port)
            server_version = info.version
            device = info.device
            all_updatable_models.add(device.model)

            # Fall back anyway if we're only supposed to affect the module
            # we're directly connected to, and not any of the submodules
            # controlled by it.
            if slot_index == CMM_SLOT_INDEX:
                fall_back_to_cfg_man = True
                if not quiet:
                    log.info(
                        "Application is responsive, but connecting to "
                        "configuration manager anyway, such that only the "
                        "management module is updated."
                    )

            # Fall back anyway if the application doesn't support the
            # configuration command set.
            elif "legacy" in info.protocol:
                fall_back_to_cfg_man = True
                if not quiet:
                    log.info("Application is responsive, but doesn't support configuration yet.")

        # Fall back to configuration manager if needed.
        if fall_back_to_cfg_man:
            if not quiet:
                log.info("Trying to connect to configuration manager (port %d)...", cfg_port)

            info = None
            try:
                info = probe_port(address, cfg_port, client_version, 3.0)
            except Exception as e:
                fall_back_to_cmm = True
                if slot_index is None:
                    raise RuntimeError(
                        f'Failed to connect to "{identifier}", determined to be at {address}.'
                    )
                if not quiet:
                    log.info(
                        "Failed to connect to configuration manager (%s), falling back to CMM.",
                        e,
                    )
            if info is not None:
                # Update connection information.
                protocol = "legacy" if "legacy" in info.protocol else "scpi"
                full_address = (address, cfg_port)
                server_version = info.version
                if device is None:
                    device = info.device
                else:
                    description = device.to_dict()
                    description.update(info.device.to_dict())
                    device = DeviceInfo.from_dict(description)
                all_updatable_models.add(device.model)
            # If connection to the configuration manager fails and slot_index is
            # provided, try to reach via CMM.
            if fall_back_to_cmm and slot_index is not None:
                try:
                    # Resolve the CMM address and port.
                    info = resolve(address)
                    address = info.address
                    app_port = info.scpi_port
                    if not quiet:
                        log.info("Trying to connect to application (port %d)...", app_port)
                    # Connect to CMM and retrieve module information.
                    info = probe_port(address, app_port, client_version, 1.0, slot_index)
                    protocol = "scpi"
                    full_address = (address, app_port)
                    server_version = info.version
                    device = info.device
                    all_updatable_models.add(device.model)
                except Exception as e:
                    if not quiet:
                        log.info("Failed to connect to CMM application (%s)", e)
                    raise RuntimeError(
                        f"Failed to connect to CMM application ({e}), which was "
                        f"determined to be at '{identifier}'."
                    )
    else:
        assert False

    # Get some additional information if this is a fully-featured SCPI
    # connection.
    if protocol == "scpi" and not fall_back_to_cmm:
        with IpTransport(full_address[0], full_address[1], 3.0) as t:
            cm = CfgMan(t)

            # Read name from device.
            if device.name == "unknown":
                device.update_name(cm.get_name())

            # Read current IP configuration from device.
            ip_config = cm.get_ip_config()

            # Read module types.
            module_types = cm._get_update_module_types()
            if module_types != "not_applicable":
                all_updatable_models.update(module_types.split(","))

    # Warn if trying to configure an entire cluster when the CMM is not yet
    # capable of doing that.
    if protocol == "legacy" and device.model == "cluster_mm" and slot_index is None:
        if not quiet:
            log.warn(
                "The current version of the software running on the "
                "connected cluster management module (CMM) cannot "
                "automatically update or roll back the other modules in the "
                "cluster. To do that, CMM will need to be updated first. So, "
                "in order to update the entire cluster, you will need to run "
                "the updater twice."
            )
        slot_index = CMM_SLOT_INDEX

    # Warn if the user is trying to configure only the cluster management
    # module of a cluster, when the device we're connecting to is not a
    # cluster management module.
    if slot_index == CMM_SLOT_INDEX and device.model != "cluster_mm":
        if not quiet:
            log.warn(
                "Scope was restricted to the cluster management module, but "
                "the device we're connecting to is not a cluster."
            )
        slot_index = None

    # Add the module suffix back onto the identifier.
    if slot_index is not None:
        identifier = f"{identifier}/{slot_index}"

    # Build and return connection information structure.
    return ConnectionInfo(
        identifier,
        protocol,
        full_address,
        slot_index,
        ip_config,
        server_version,
        client_version,
        device,
        all_updatable_models,
    )


# ----------------------------------------------------------------------------
def get_device_info(identifier: Union[str, AddressInfo, ConnectionInfo]) -> DeviceInfo:
    """
    Fetches a complete :class:`~qblox_instruments.DeviceInfo` structure for
    the given device.

    Parameters
    ----------
    identifier: Union[str, AddressInfo, ConnectionInfo]
        Instrument identifier. See :func:`~qblox_instruments.resolve()` for
        more information.

    Returns
    -------
    DeviceInfo
        The device information.

    Raises
    ------
    RuntimeError
        if we failed to connect.
    """
    return probe_device(identifier, quiet=True).device
