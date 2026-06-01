"""Windows-specific helpers for capture readiness."""

import ctypes
import sys


def is_windows() -> bool:
    return sys.platform == "win32"


def is_admin() -> bool:
    if not is_windows():
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def list_network_interfaces() -> list[str]:
    try:
        from scapy.interfaces import ifaces

        names: list[str] = []
        for iface in ifaces.values():
            name = getattr(iface, "name", None) or getattr(iface, "network_name", None)
            if name and name not in names:
                names.append(str(name))
        if names:
            return sorted(names)
    except Exception:
        pass

    try:
        from scapy.all import get_if_list

        return sorted(get_if_list())
    except Exception:
        return []


def capture_readiness_message() -> str | None:
    """Return a user-facing warning, or None if capture looks possible."""
    ifaces = list_network_interfaces()
    if not ifaces:
        return (
            "No network interfaces found. Install Npcap (https://npcap.com/) "
            "and restart the application."
        )
    if is_windows() and not is_admin():
        return (
            "Live capture usually requires running this application as Administrator "
            "on Windows."
        )
    return None
