import logging
import re
import subprocess
import sys


def check_ping(target, timeout_seconds):
    """Prueft die Erreichbarkeit und liefert die Latenz in Millisekunden."""
    if sys.platform.startswith("win"):
        command = [
            "ping", "-n", "1", "-w", str(timeout_seconds * 1000), target
        ]
    else:
        command = [
            "ping", "-c", "1", "-W", str(timeout_seconds), target
        ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds + 1,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        logging.warning("Ping konnte nicht ausgefuehrt werden: %s", error)
        return None

    if result.returncode != 0:
        return None

    output = result.stdout + result.stderr
    match = re.search(r"time[=<]([0-9]+(?:[.,][0-9]+)?)", output)
    if not match:
        return 0.0

    return float(match.group(1).replace(",", "."))
