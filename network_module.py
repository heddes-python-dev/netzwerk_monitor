import psutil


def collect_network_data():
    """Liest Zaehler und Status der Netzwerkinterfaces aus."""
    counters = psutil.net_io_counters(pernic=True)
    interface_stats = psutil.net_if_stats()
    interfaces = []

    for name, counter in counters.items():
        stats = interface_stats.get(name)
        interfaces.append({
            "name": name,
            "is_up": bool(stats and stats.isup),
            "speed_mbps": stats.speed if stats else 0,
            "bytes_sent": counter.bytes_sent,
            "bytes_recv": counter.bytes_recv,
            "packets_sent": counter.packets_sent,
            "packets_recv": counter.packets_recv,
        })

    active_interfaces = [item for item in interfaces if item["is_up"]]
    return {
        "interfaces": interfaces,
        "active_interfaces": len(active_interfaces),
        "bytes_sent": sum(item["bytes_sent"] for item in interfaces),
        "bytes_recv": sum(item["bytes_recv"] for item in interfaces),
    }
