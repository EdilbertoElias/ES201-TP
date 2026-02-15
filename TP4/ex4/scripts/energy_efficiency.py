#!/usr/bin/env python3
import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple

IPC_RE = re.compile(r"^system\.cpu\.ipc\s+([0-9.]+)")
SIZE_ORDER = {"1kB": 1, "2kB": 2, "4kB": 4, "8kB": 8, "16kB": 16, "32kB": 32}
POWER_MW = {"A7": 100.0, "A15": 500.0}
SIZES_KB = [1, 2, 4, 8, 16, 32]
SIZE_LABELS = {1: "1kB", 2: "2kB", 4: "4kB", 8: "8kB", 16: "16kB", 32: "32kB"}


def parse_ipc(stats_path: Path) -> float:
    with stats_path.open() as f:
        for line in f:
            match = IPC_RE.match(line)
            if match:
                return float(match.group(1))
    raise ValueError(f"IPC not found in {stats_path}")


def collect_data(root: Path) -> Dict[str, Dict[str, List[Tuple[str, float, float]]]]:
    data: Dict[str, Dict[str, List[Tuple[str, float, float]]]] = {}
    inputs = [
        ("A7", root / "m5out_A7"),
        ("A15", root / "m5out_A15"),
    ]

    for cpu, base in inputs:
        power = POWER_MW[cpu]
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
            eff = ipc / power
            data.setdefault(app, {}).setdefault(cpu, []).append((size, ipc, eff))

    for app in data:
        for cpu in data[app]:
            data[app][cpu].sort(key=lambda x: SIZE_ORDER.get(x[0], 999))

    return data


def write_csv(out_dir: Path, data: Dict[str, Dict[str, List[Tuple[str, float, float]]]]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for app in data:
        out_path = out_dir / f"{app}_energy_efficiency.csv"
        with out_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["l1_size", "cpu", "ipc", "power_mw", "efficiency_ipc_per_mw"])
            for cpu in ["A7", "A15"]:
                power = POWER_MW[cpu]
                for size, ipc, eff in data[app][cpu]:
                    writer.writerow([size, cpu, f"{ipc:.6f}", f"{power:.0f}", f"{eff:.6f}"])


def plot(app: str, data: Dict[str, Dict[str, List[Tuple[str, float, float]]]], out_dir: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit("matplotlib not installed. Install it and re-run this script.") from exc

    fig, ax = plt.subplots(figsize=(10.0, 6.0), dpi=150)

    style = {
        "A7": {"color": "#1f77b4", "marker": "o", "linestyle": "-"},
        "A15": {"color": "#d62728", "marker": "o", "linestyle": "-"},
    }

    sizes_union = set()
    for cpu in ["A7", "A15"]:
        if cpu not in data[app]:
            continue
        sizes = [SIZE_ORDER[s] for s, _, _ in data[app][cpu]]
        effs = [eff for _, _, eff in data[app][cpu]]
        sizes_union.update(sizes)
        ax.plot(
            sizes,
            effs,
            label=cpu,
            color=style[cpu]["color"],
            marker=style[cpu]["marker"],
            linestyle=style[cpu]["linestyle"],
            linewidth=2,
        )

    ax.set_title(f"Energy efficiency vs L1 size ({app})", fontsize=14)
    ax.set_xlabel("Cache size (kB)", fontsize=12)
    ax.set_ylabel("Efficiency (IPC/mW)", fontsize=12)
    ax.grid(True, which="both", linestyle="--", alpha=0.7)
    ax.set_xscale("log", base=2)
    ax.set_xticks(sorted(sizes_union) or SIZES_KB)
    ax.set_xticklabels([SIZE_LABELS.get(x, f"{x}kB") for x in (sorted(sizes_union) or SIZES_KB)])
    ax.legend(fontsize=11)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{app}_energy_efficiency.png"
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_by_cpu(cpu: str, data: Dict[str, Dict[str, List[Tuple[str, float, float]]]], out_dir: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit("matplotlib not installed. Install it and re-run this script.") from exc

    fig, ax = plt.subplots(figsize=(10.0, 6.0), dpi=150)

    style = {
        "dijkstra": {"color": "#1f77b4", "marker": "o", "linestyle": "-"},
        "blowfish": {"color": "#d62728", "marker": "o", "linestyle": "-"},
    }

    sizes_union = set()
    for app in data:
        if cpu not in data[app]:
            continue
        sizes = [SIZE_ORDER[s] for s, _, _ in data[app][cpu]]
        effs = [eff for _, _, eff in data[app][cpu]]
        sizes_union.update(sizes)
        ax.plot(
            sizes,
            effs,
            label=app,
            color=style.get(app, {"color": "#1f77b4"})["color"],
            marker=style.get(app, {"marker": "o"})["marker"],
            linestyle=style.get(app, {"linestyle": "-"})["linestyle"],
            linewidth=2,
        )

    ax.set_title(f"Energy efficiency vs L1 size ({cpu})", fontsize=14)
    ax.set_xlabel("Cache size (kB)", fontsize=12)
    ax.set_ylabel("Efficiency (IPC/mW)", fontsize=12)
    ax.grid(True, which="both", linestyle="--", alpha=0.7)
    ax.set_xscale("log", base=2)
    ax.set_xticks(sorted(sizes_union) or SIZES_KB)
    ax.set_xticklabels([SIZE_LABELS.get(x, f"{x}kB") for x in (sorted(sizes_union) or SIZES_KB)])
    ax.legend(fontsize=11)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{cpu.lower()}_energy_efficiency_by_app.png"
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "plots"

    data = collect_data(root)
    write_csv(out_dir, data)

    for app in ["dijkstra", "blowfish"]:
        if app in data:
            plot(app, data, out_dir)

    for cpu in ["A7", "A15"]:
        plot_by_cpu(cpu, data, out_dir)


if __name__ == "__main__":
    main()
