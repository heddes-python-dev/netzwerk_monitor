import logging
from tkinter import messagebox

import config


def zeige_popup(titel, nachricht, parent=None):
    """Zeigt ein Warnfenster, sofern es aktiviert ist."""
    if not config.POPUP_AKTIVIERT:
        return

    try:
        messagebox.showwarning(titel, nachricht, parent=parent)
    except Exception as error:
        logging.error("Popup konnte nicht angezeigt werden: %s", error, exc_info=True)
