#!/usr/bin/env python3
import re
from pathlib import Path

IPC_RE = re.compile(r"^system\.cpu\.ipc\s+([0-9.]+)")


def parse_ipc(stats_path: Path) -> float:
    with stats_path.open() as f:
        for line in f:
            match = IPC_RE.match(line)
            if match:
                return float(match.group(1))
    raise ValueError(f"IPC not found in {stats_path}")


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    inputs = [
        ("A7", root / "m5out_A7"),
        ("A15", root / "m5out_A15"),
    ]

    results = []
    for cpu, base in inputs:
        for entry in sorted(base.iterdir()):
            if not entry.is_dir():
                continue
            stats = entry / "stats.txt"
            if not stats.exists():
                continue
            ipc = parse_ipc(stats)
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
            results.append((app, cpu, size, ipc))

    for app, cpu, size, ipc in results:
        print(app, cpu, size, f"{ipc:.6f}")


if __name__ == "__main__":
    main()
