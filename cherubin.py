import psutil
import time
import argparse
import traceback
import logging
from rich.console import Console, Group
from rich.table import Table
from rich.live import Live

logging.basicConfig(
    filename="Cherubin_error.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
console = Console()

parser = argparse.ArgumentParser(description="Cherubin Live Network Monitor")
parser.add_argument("--top", type=int, default=5)
parser.add_argument("--alert_mbps", type=float, default=50.0)
parser.add_argument("--refresh", type=float, default=1.0)
args = parser.parse_args()

TOP_N = args.top
ALERT_MBPS = args.alert_mbps
REFRESH = max(0.2, float(args.refresh))

BAR_LENGTH = 26
NUMBER_WIDTH = 12

def human_readable_bytes(b):
    if b < 1024:
        return f"{b} B"
    kb = b / 1024
    if kb < 1024:
        return f"{kb:.2f} KB"
    mb = kb / 1024
    if mb < 1024:
        return f"{mb:.2f} MB"
    gb = mb / 1024
    return f"{gb:.2f} GB"

def colorize_mbps(value):
    if value > ALERT_MBPS:
        return f"[red]{value:.2f}[/red]"
    elif value > ALERT_MBPS * 0.5:
        return f"[yellow]{value:.2f}[/yellow]"
    else:
        return f"[green]{value:.2f}[/green]"

def bar(value, max_value, length=BAR_LENGTH):
    if value <= 0:
        return " " * length
    ratio = min(value / max_value, 1.0)
    filled = int(round(length * ratio))
    empty = length - filled
    if ratio > 0.75:
        color = "red"
    elif ratio > 0.5:
        color = "yellow"
    else:
        color = "green"
    return f"[{color}]" + "|" * filled + "[/]" + " " * empty

def build_interface_tables(prev_stats):
    stats = psutil.net_io_counters(pernic=True)
    
    # Tabela Transferu – nagłówek złączony dla paska + liczby
    t1 = Table(title="Transfer", expand=True, show_header=True)
    t1.add_column("Interface", style="cyan", min_width=20)
    t1.add_column("Upload", justify="left", min_width=BAR_LENGTH + NUMBER_WIDTH)
    t1.add_column("Download", justify="left", min_width=BAR_LENGTH + NUMBER_WIDTH)
    
    t2 = Table(title="Speed & Packets", expand=True, show_header=True)
    t2.add_column("Interface", style="cyan", min_width=20)
    t2.add_column("Sent Mbps", justify="right", min_width=12)
    t2.add_column("Recv Mbps", justify="right", min_width=12)
    t2.add_column("Sent Pkts", justify="right", min_width=10)
    t2.add_column("Recv Pkts", justify="right", min_width=10)

    for iface, vals in stats.items():
        prev = prev_stats.get(iface, {"bytes_sent":0, "bytes_recv":0, "packets_sent":0, "packets_recv":0})
        delta_sent = vals.bytes_sent - prev["bytes_sent"]
        delta_recv = vals.bytes_recv - prev["bytes_recv"]
        delta_sent_pkts = vals.packets_sent - prev["packets_sent"]
        delta_recv_pkts = vals.packets_recv - prev["packets_recv"]
        sent_mbps = delta_sent * 8 / REFRESH / 1e6
        recv_mbps = delta_recv * 8 / REFRESH / 1e6

        # Łączymy pasek i wartość w jednej kolumnie
        up_val = f"{bar(sent_mbps, ALERT_MBPS*2)}{human_readable_bytes(delta_sent):>{NUMBER_WIDTH}}"
        down_val = f"{bar(recv_mbps, ALERT_MBPS*2)}{human_readable_bytes(delta_recv):>{NUMBER_WIDTH}}"

        t1.add_row(iface, up_val, down_val)

        row_style = None
        if sent_mbps > ALERT_MBPS or recv_mbps > ALERT_MBPS:
            row_style = "bold red"
        elif sent_mbps > ALERT_MBPS * 0.5 or recv_mbps > ALERT_MBPS * 0.5:
            row_style = "bold yellow"

        t2.add_row(
            iface,
            colorize_mbps(sent_mbps),
            colorize_mbps(recv_mbps),
            str(delta_sent_pkts),
            str(delta_recv_pkts),
            style=row_style
        )

        prev_stats[iface] = {
            "bytes_sent": vals.bytes_sent,
            "bytes_recv": vals.bytes_recv,
            "packets_sent": vals.packets_sent,
            "packets_recv": vals.packets_recv
        }

    return t1, t2

def build_top_ips():
    conns = psutil.net_connections(kind="inet")
    agg = {}
    for c in conns:
        if c.raddr:
            ip = c.raddr.ip
            agg[ip] = agg.get(ip, 0) + 1
    top = sorted(agg.items(), key=lambda x: x[1], reverse=True)[:TOP_N]

    t = Table(title=f"Top Remote IPs (top {TOP_N})", expand=True, show_header=True)
    t.add_column("Remote IP", style="magenta", min_width=20)
    t.add_column("Connections", justify="right", min_width=10)
    if not top:
        t.add_row("-", "0")
    else:
        for ip, cnt in top:
            t.add_row(ip, str(cnt))
    return t

def main():
    prev_stats = {}
    with Live(console=console, refresh_per_second=4, screen=False) as live:
        while True:
            try:
                t1, t2 = build_interface_tables(prev_stats)
                ip_table = build_top_ips()
                layout = Group(t1, t2, ip_table)
                live.update(layout)
                time.sleep(REFRESH)

            except KeyboardInterrupt:
                console.print("\nExiting Cherubin...", style="bold yellow")
                break
            except Exception:
                logging.error(traceback.format_exc())
                console.print("Error! Check Cherubin_error.log", style="red")
                time.sleep(1)

if __name__ == "__main__":
    main()