import logging
from logging.handlers import RotatingFileHandler

LOG_DATEI = "netzwerk_monitor.log"
INTERVALL_SEKUNDEN = 5
PING_ZIEL = "1.1.1.1"
PING_TIMEOUT_SEKUNDEN = 2
LATENZ_SCHWELLENWERT_MS = 200
WARNUNG_NACH_MESSUNGEN = 2
POPUP_AKTIVIERT = False


def setup_logging():
    """Konfiguriert das Logging genau einmal."""
    logger = logging.getLogger()
    if any(getattr(handler, "netzwerk_monitor_handler", False)
           for handler in logger.handlers):
        return

    handler = RotatingFileHandler(
        LOG_DATEI,
        maxBytes=1 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    ))
    handler.netzwerk_monitor_handler = True
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
