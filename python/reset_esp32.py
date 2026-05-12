#!/usr/bin/env python3
"""Reset an ESP32 dev board through serial modem-control lines.

This uses only the Python standard library. It expects the common ESP32
auto-reset circuit where RTS pulses EN low and DTR stays deasserted so GPIO0
remains high for normal boot.
"""

from __future__ import annotations

import argparse
import array
import os
import sys
import time

try:
    import fcntl
    import termios
except ImportError as exc:
    fcntl = None
    termios = None
    MODEM_CONTROL_IMPORT_ERROR = exc
else:
    MODEM_CONTROL_IMPORT_ERROR = None


def _set_modem_lines(fd: int, *, dtr: bool | None = None, rts: bool | None = None) -> None:
    flags = array.array("i", [0])
    fcntl.ioctl(fd, termios.TIOCMGET, flags, True)
    value = flags[0]

    if dtr is not None:
        if dtr:
            value |= termios.TIOCM_DTR
        else:
            value &= ~termios.TIOCM_DTR

    if rts is not None:
        if rts:
            value |= termios.TIOCM_RTS
        else:
            value &= ~termios.TIOCM_RTS

    flags[0] = value
    fcntl.ioctl(fd, termios.TIOCMSET, flags)


def reset_esp32(port: str, pulse_sec: float, settle_sec: float) -> None:
    if MODEM_CONTROL_IMPORT_ERROR is not None:
        raise RuntimeError(
            "ESP32 reset through serial modem-control lines requires POSIX "
            "fcntl/termios support, which is unavailable on this platform."
        ) from MODEM_CONTROL_IMPORT_ERROR

    fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    try:
        _set_modem_lines(fd, dtr=False, rts=False)
        time.sleep(0.05)
        _set_modem_lines(fd, dtr=False, rts=True)
        time.sleep(pulse_sec)
        _set_modem_lines(fd, dtr=False, rts=False)
        time.sleep(settle_sec)
    finally:
        os.close(fd)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pulse an ESP32 reset line through a serial adapter."
    )
    parser.add_argument("--port", required=True, help="Serial device, e.g. /dev/serial-port")
    parser.add_argument("--pulse-sec", type=float, default=0.2, help="RTS reset pulse length")
    parser.add_argument("--settle-sec", type=float, default=2.0, help="Delay after reset")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.pulse_sec <= 0:
        print("error: --pulse-sec must be positive", file=sys.stderr)
        return 2
    if args.settle_sec < 0:
        print("error: --settle-sec must be non-negative", file=sys.stderr)
        return 2

    try:
        reset_esp32(args.port, args.pulse_sec, args.settle_sec)
    except OSError as exc:
        print(f"error: could not reset ESP32 on {args.port}: {exc}", file=sys.stderr)
        return 1
    except AttributeError as exc:
        print(f"error: modem-control ioctl is unavailable on this platform: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"ESP32 reset pulse sent on {args.port}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
