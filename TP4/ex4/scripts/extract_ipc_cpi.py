#!/usr/bin/env python3
import re
from pathlib import Path

IPC_RE = re.compile(r"^system\.cpu\.ipc\s+([0-9.]+)")
CPI_RE = re.compile(r"^system\.cpu\.cpi\s+([0-9.]+)")
SIZE_ORDER = {"1kB": 1, "2kB": 2, "4kB": 4, "8kB": 8, "16kB": 16, "32kB": 32}


def parse_stats(stats_path: Path):
    ipc = None
    cpi = None
    with stats_path.open() as f:
        for line in f:
            if ipc is None:
                match = IPC_RE.match(line)
                if match:
                    ipc = float(match.group(1))
            if cpi is None:
                match = CPI_RE.match(line)
                if match:
                    cpi = float(match.group(1))
            if ipc is not None and cpi is not None:
                break
    return ipc, cpi


def collect(root: Path):
    results = []
    for cpu, base in [("A7", root / "m5out_A7"), ("A15", root / "m5out_A15")]:
        for entry in sorted(base.iterdir()):
            if not entry.is_dir():
                continue
            stats = entry / "stats.txt"
            if not stats.exists():
                continue
            ipc, cpi = parse_stats(stats)
            name = entry.name
            if name.startswith("blowfish_"):
                app = "blowfish"
                size = name.replace("blowfish_size_", "")
            elif name.startswith("size_"):
                app = "dijkstra"
                size = name.replace("size_", "")
            else:
                app = "unknown"
                size = name
            results.append((app, cpu, size, ipc, cpi))

    results.sort(key=lambda x: (x[0], x[1], SIZE_ORDER.get(x[2], 999)))
    return results


def print_markdown_tables(results):
    for app in ["dijkstra", "blowfish"]:
        print(f"\n{app.upper()} (IPC/CPI)")
        print("| L1 size | CPU | IPC | CPI |")
        print("|---|---|---:|---:|")
        for a, cpu, size, ipc, cpi in results:
            if a != app:
                continue
            print(f"| {size} | {cpu} | {ipc:.6f} | {cpi:.6f} |")


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    results = collect(root)
    print_markdown_tables(results)


if __name__ == "__main__":
    main()
