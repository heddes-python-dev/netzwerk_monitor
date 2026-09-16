import logging
import queue
import threading
import time

import config
from gui_module import starte_gui
from network_module import collect_network_data
from ping_module import check_ping
from popup_module import zeige_popup

config.setup_logging()

stop_event = threading.Event()
popup_queue = queue.Queue()
status_queue = queue.Queue(maxsize=1)


def publish_status(status):
    """Haelt nur den aktuellsten Messwert fuer die GUI bereit."""
    try:
        status_queue.get_nowait()
        status_queue.task_done()
    except queue.Empty:
        pass

    try:
        status_queue.put_nowait(status)
    except queue.Full:
        pass


def format_rate(bytes_per_second):
    if bytes_per_second >= 1024 * 1024:
        return f"{bytes_per_second / (1024 * 1024):.1f} MB/s"
    return f"{bytes_per_second / 1024:.1f} KB/s"


def monitor_loop():
    logging.info("Netzwerkueberwachung gestartet.")
    previous_data = None
    previous_time = None
    consecutive_warnings = 0
    warning_active = False

    while not stop_event.is_set():
        try:
            now = time.monotonic()
            data = collect_network_data()
            latency = check_ping(
                config.PING_ZIEL,
                config.PING_TIMEOUT_SEKUNDEN,
            )

            upload_rate = 0.0
            download_rate = 0.0
            if previous_data is not None and previous_time is not None:
                elapsed = max(now - previous_time, 0.001)
                upload_rate = max(
                    data["bytes_sent"] - previous_data["bytes_sent"], 0
                ) / elapsed
                download_rate = max(
                    data["bytes_recv"] - previous_data["bytes_recv"], 0
                ) / elapsed

            previous_data = data
            previous_time = now
            status = {
                "connected": latency is not None,
                "latency": latency,
                "upload_rate": upload_rate,
                "download_rate": download_rate,
                "active_interfaces": data["active_interfaces"],
            }
            publish_status(status)

            warnings = []
            if latency is None:
                warnings.append("Keine Verbindung zu " + config.PING_ZIEL)
            elif latency > config.LATENZ_SCHWELLENWERT_MS:
                warnings.append(f"Hohe Latenz ({latency:.1f} ms)")

            if warnings:
                consecutive_warnings += 1
            else:
                consecutive_warnings = 0
                warning_active = False

            if (
                warnings
                and consecutive_warnings >= config.WARNUNG_NACH_MESSUNGEN
                and not warning_active
            ):
                warning_active = True
                message = ", ".join(warnings)
                logging.warning("NETZWERK-WARNUNG: %s", message)
                popup_queue.put(("Netzwerk Monitor Alarm!", message))
            elif not warnings:
                logging.info(
                    "Verbindung OK, Latenz: %s ms, aktive Interfaces: %s",
                    f"{latency:.1f}" if latency is not None else "nicht verfuegbar",
                    data["active_interfaces"],
                )
        except Exception as error:
            logging.error("Fehler im Netzwerkmonitor: %s", error, exc_info=True)

        stop_event.wait(config.INTERVALL_SEKUNDEN)

    logging.info("Netzwerkueberwachung beendet.")


def process_queues(root, labels):
    try:
        while True:
            title, message = popup_queue.get_nowait()
            zeige_popup(title, message, parent=root)
            popup_queue.task_done()
    except queue.Empty:
        pass

    try:
        while True:
            status = status_queue.get_nowait()
            labels["connection"].config(
                text="Verbindung: OK" if status["connected"] else "Verbindung: getrennt"
            )
            latency = status["latency"]
            labels["latency"].config(
                text=f"Latenz: {latency:.1f} ms" if latency is not None else "Latenz: --"
            )
            labels["upload"].config(
                text=f"Upload: {format_rate(status['upload_rate'])}"
            )
            labels["download"].config(
                text=f"Download: {format_rate(status['download_rate'])}"
            )
            labels["interfaces"].config(
                text=f"Aktive Interfaces: {status['active_interfaces']}"
            )
            status_queue.task_done()
    except queue.Empty:
        pass

    if not stop_event.is_set():
        root.after(100, lambda: process_queues(root, labels))


def on_closing(root):
    logging.info("Netzwerkmonitor wird geschlossen.")
    stop_event.set()
    root.destroy()


if __name__ == "__main__":
    logging.info("Netzwerk Monitor mit Live-GUI wird gestartet.")
    root, labels = starte_gui(on_closing)
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()
    root.after(100, lambda: process_queues(root, labels))
    root.mainloop()
    monitor_thread.join(timeout=2)
    logging.info("Netzwerkmonitor vollstaendig heruntergefahren.")
