"""Network detection and connectivity monitoring."""

from __future__ import annotations

import socket
import time
from datetime import UTC, datetime

from ke.core.models import NetworkState


class NetworkDetector:
    """Detect network state and connectivity quality."""

    def __init__(
        self,
        check_interval: int = 30,
        quality_threshold_latency_ms: float = 500.0,
        probes: list[str] | None = None,
    ):
        self.check_interval = check_interval
        self.quality_threshold_latency_ms = quality_threshold_latency_ms
        self.probes = probes or ["dns", "http"]
        self._last_state: NetworkState | None = None
        self._last_check: float = 0

    def detect(self, force: bool = False) -> NetworkState:
        """Detect current network state."""
        now = time.time()
        if not force and self._last_state and (now - self._last_check) < self.check_interval:
            return self._last_state

        interfaces = self._get_interfaces()
        status = "offline"
        latency_ms = None
        bandwidth_mbps = None

        if interfaces:
            # Try DNS resolution
            if "dns" in self.probes:
                dns_ok = self._check_dns()
                if dns_ok:
                    status = "wifi"  # Assume wifi if DNS works

            # Try HTTP probe
            if "http" in self.probes and status != "offline":
                latency_ms = self._check_http_latency()
                if latency_ms is not None:
                    if latency_ms > self.quality_threshold_latency_ms:
                        status = "poor"
                    elif latency_ms > self.quality_threshold_latency_ms / 2:
                        status = "limited"
                    # Otherwise keep wifi status

        state = NetworkState(
            status=status,
            interfaces=interfaces,
            latency_ms=latency_ms,
            bandwidth_mbps=bandwidth_mbps,
            last_checked=datetime.now(tz=UTC),
        )

        self._last_state = state
        self._last_check = now
        return state

    def _get_interfaces(self) -> list[str]:
        """Get active network interfaces."""
        interfaces = []
        try:
            import netifaces

            for iface in netifaces.interfaces():
                # Skip loopback
                if iface == "lo" or iface.startswith("lo"):
                    continue

                addrs = netifaces.ifaddresses(iface)
                # Check for IPv4 or IPv6 addresses
                if netifaces.AF_INET in addrs or netifaces.AF_INET6 in addrs:
                    interfaces.append(iface)
        except ImportError:
            # Fallback: try socket method
            try:
                hostname = socket.gethostname()
                addrs = socket.getaddrinfo(hostname, None)
                for addr in addrs:
                    if addr[0] in (socket.AF_INET, socket.AF_INET6):
                        interfaces.append(addr[4][0])
            except Exception:
                pass

        return interfaces

    def _check_dns(self) -> bool:
        """Check if DNS resolution works."""
        try:
            socket.getaddrinfo("google.com", 80)
            return True
        except (socket.gaierror, OSError):
            return False

    def _check_http_latency(self) -> float | None:
        """Check HTTP latency to a known endpoint."""
        import requests

        endpoints = [
            "https://www.google.com",
            "https://1.1.1.1",
            "https://httpbin.org/get",
        ]

        for endpoint in endpoints:
            try:
                start = time.time()
                requests.get(endpoint, timeout=5)
                latency_ms = (time.time() - start) * 1000
                return latency_ms
            except Exception:
                continue

        return None

    def is_online(self) -> bool:
        """Quick check if we're online."""
        state = self.detect()
        return state.status != "offline"

    def is_offline(self) -> bool:
        """Quick check if we're offline."""
        return not self.is_online()
