# Netzwerk Monitor

Ein modularer Netzwerkmonitor nach dem gleichen Architekturprinzip wie der System Monitor. Die Anwendung prueft die Erreichbarkeit eines Ziels, misst die Ping-Latenz und berechnet den aktuellen Upload- und Download-Durchsatz aus den Netzwerkzaehlern der lokalen Interfaces.

Die Live-Werte werden in einer thread-sicheren Tkinter-GUI angezeigt. Bei einem Verbindungsverlust oder zu hoher Latenz kann der Monitor eine Warnung protokollieren und optional ein Popup anzeigen.

## Funktionen

- Verbindungspruefung zu einem konfigurierbaren Ping-Ziel
- Ping-Latenz in Millisekunden
- Upload- und Download-Durchsatz in KB/s oder MB/s
- Anzahl aktiver Netzwerkinterfaces
- Erkennung von Verbindungsverlust
- Warnung bei dauerhaft hoher Latenz
- Thread-sichere Kommunikation zwischen Worker und GUI
- Entprellte Warnungen gegen kurze Aussetzer
- Rotierendes Logfile mit drei Sicherungsdateien
- PyInstaller-Spezifikation fuer eine eigenstaendige Anwendung

## Architektur

```text
netzwerk_monitor/
├── main.py              Worker, Queues und Programmablauf
├── config.py            Einstellungen und Logging
├── network_module.py    Interface-Status und Netzwerkzaehler
├── ping_module.py       Plattformabhaengiger Ping-Test
├── gui_module.py        Tkinter-Live-Oberflaeche
├── popup_module.py      Optionale Warnfenster
└── main.spec            PyInstaller-Konfiguration
```

Der Worker sammelt die Zaehler und Ping-Werte im Hintergrund. Die GUI wird ausschliesslich im Tkinter-Hauptthread aktualisiert. Die Status-Queue behaelt nur den neuesten Datensatz, damit sich bei einer blockierten GUI keine alten Messwerte stapeln.

## Voraussetzungen

- Python 3.10 oder neuer
- `psutil`
- Tkinter
- Das Systemprogramm `ping`

Unter Debian/Ubuntu:

```bash
sudo apt install python3-tk iputils-ping
```

Python-Abhaengigkeit installieren:

```bash
python3 -m pip install psutil
```

## Start

```bash
cd .../netzwerk_monitor
python3 main.py
```

Das Standardziel fuer den Ping-Test ist `1.1.1.1`.

## Konfiguration

Die Einstellungen stehen in [config.py](config.py):

| Einstellung | Bedeutung | Aktueller Wert |
|---|---|---:|
| `INTERVALL_SEKUNDEN` | Zeit zwischen Messungen | `5` |
| `PING_ZIEL` | Ziel fuer den Erreichbarkeitstest | `1.1.1.1` |
| `PING_TIMEOUT_SEKUNDEN` | Maximale Wartezeit fuer einen Ping | `2` |
| `LATENZ_SCHWELLENWERT_MS` | Latenz-Warnschwelle | `200` |
| `WARNUNG_NACH_MESSUNGEN` | Benoetigte aufeinanderfolgende Warnmessungen | `2` |
| `POPUP_AKTIVIERT` | Optionale Warnfenster | `False` |

Fuer ein lokales Netzwerk kann `PING_ZIEL` beispielsweise auf die Adresse des Routers gesetzt werden:

```python
PING_ZIEL = "192.168.1.1"
```

## Messung des Durchsatzes

`network_module.py` liest die kumulativen Byte-Zaehler von psutil. `main.py` vergleicht zwei Messungen und teilt die Differenz durch die vergangene Zeit:

```text
Durchsatz = (neuer Zaehler - alter Zaehler) / vergangene Sekunden
```

Beim ersten Messzyklus gibt es noch keinen Vergleichswert. Deshalb wird der Durchsatz anfangs mit `0.0` angezeigt.

## Logging

Die Anwendung schreibt nach `netzwerk_monitor.log`. Die Datei wird bei 1 MB rotiert; bis zu drei Backups bleiben erhalten.

Das Log enthaelt:

- Start und Ende der Netzwerkueberwachung
- erfolgreiche Verbindungen und Latenzen
- Warnungen bei hoher Latenz oder fehlender Verbindung
- Fehler inklusive Stacktrace

## Build mit PyInstaller

Aus dem Unterverzeichnis:

```bash
python3 -m pip install pyinstaller
pyinstaller main.spec
```

Das Ergebnis liegt anschliessend in `dist/`.

## Bekannte Grenzen

- Der Ping-Test benoetigt das Systemprogramm `ping` und eine erlaubte Netzwerkverbindung.
- Ein einzelnes Ping-Ziel kann ausfallen, obwohl das Internet grundsaetzlich erreichbar ist.
- Der Durchsatz wird ueber alle Interfaces summiert; virtuelle Interfaces koennen das Ergebnis beeinflussen.
- Es gibt derzeit keine historische Aufzeichnung und keine Diagramme.
- Die Anwendung misst keinen Paketverlust ueber mehrere Ping-Versuche.

## Lizenz

Dieses Projekt enthaelt derzeit keine separate Lizenzdatei.
