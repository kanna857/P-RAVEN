import socket
import ipaddress
import urllib.parse
from typing import Tuple

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # RFC1918 Private
    ipaddress.ip_network("172.16.0.0/12"),    # RFC1918 Private
    ipaddress.ip_network("192.168.0.0/16"),   # RFC1918 Private
    ipaddress.ip_network("169.254.0.0/16"),   # Link-Local & Cloud Metadata (169.254.169.254)
    ipaddress.ip_network("0.0.0.0/8"),        # Current network
    ipaddress.ip_network("224.0.0.0/4"),      # Multicast
    ipaddress.ip_network("240.0.0.0/4"),      # Reserved
    ipaddress.ip_network("::1/128"),          # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 Unique Local
    ipaddress.ip_network("fe80::/10"),        # IPv6 Link Local
]

def validate_url_safety(target_url: str) -> Tuple[bool, str]:
    """
    Validates URL safety against Server-Side Request Forgery (SSRF) and private network probing.
    Returns: (is_safe, error_or_canonical_url)
    """
    if not target_url or not isinstance(target_url, str):
        return False, "Target URL is empty or invalid"

    parsed = urllib.parse.urlparse(target_url.strip())
    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Unsupported URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "URL lacks a valid hostname."

    # Prevent localhost aliases
    if hostname.lower() in ("localhost", "127.0.0.1", "::1", "metadata.google.internal"):
        return False, "Access to localhost or internal metadata hosts is strictly prohibited."

    # DNS Resolution & IP Range Check
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)

            for blocked_net in BLOCKED_IP_NETWORKS:
                if ip_obj in blocked_net:
                    return False, f"Access to private/restricted IP range ({ip_str}) is prohibited."
    except socket.gaierror:
        return False, f"Could not resolve host '{hostname}' via DNS."
    except Exception as exc:
        return False, f"SSRF security validation error: {str(exc)}"

    return True, parsed.geturl()
