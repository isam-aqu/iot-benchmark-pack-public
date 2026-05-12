#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import select
import sys
import termios
import time


BAUD_RATES = {
    value: getattr(termios, f"B{value}")
    for value in (9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600)
    if hasattr(termios, f"B{value}")
}


def open_serial(port: str, baud: int) -> int:
    if baud not in BAUD_RATES:
        supported = ", ".join(str(value) for value in sorted(BAUD_RATES))
        raise SystemExit(f"Unsupported baud {baud}; supported values: {supported}")

    fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    attrs = termios.tcgetattr(fd)
    attrs[0] = 0
    attrs[1] = 0
    attrs[2] = BAUD_RATES[baud] | termios.CS8 | termios.CLOCAL | termios.CREAD
    attrs[3] = 0
    attrs[4] = BAUD_RATES[baud]
    attrs[5] = BAUD_RATES[baud]
    attrs[6][termios.VMIN] = 0
    attrs[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    termios.tcflush(fd, termios.TCIOFLUSH)
    return fd


def write_line(fd: int, line: str) -> None:
    os.write(fd, (line.rstrip("\r\n") + "\n").encode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture a serial port to stdout, optionally writing one line after open."
    )
    parser.add_argument("--port", required=True)
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--write-line", default=None)
    parser.add_argument("--write-delay-sec", type=float, default=0.0)
    parser.add_argument("--sync-newlines", type=int, default=2)
    parser.add_argument(
        "--timeout-sec",
        type=float,
        default=0.0,
        help="Stop after this many seconds. Default 0 means capture forever.",
    )
    args = parser.parse_args()

    fd = open_serial(args.port, args.baud)
    try:
        deadline = None if args.timeout_sec <= 0 else time.monotonic() + args.timeout_sec
        if args.write_line is not None:
            if args.write_delay_sec > 0:
                time.sleep(args.write_delay_sec)
            for _ in range(max(args.sync_newlines, 0)):
                write_line(fd, "")
                time.sleep(0.05)
            write_line(fd, args.write_line)

        while True:
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                timeout = min(1.0, remaining)
            else:
                timeout = 1.0

            ready, _, _ = select.select([fd], [], [], timeout)
            if not ready:
                continue
            chunk = os.read(fd, 4096)
            if chunk:
                sys.stdout.buffer.write(chunk)
                sys.stdout.buffer.flush()
    except KeyboardInterrupt:
        pass
    finally:
        os.close(fd)


if __name__ == "__main__":
    main()
