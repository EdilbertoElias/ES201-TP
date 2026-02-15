#!/usr/bin/env python3
import os
from pathlib import Path

import matplotlib.pyplot as plt

SIZES_KB = [1, 2, 4, 8, 16, 32]
SIZES_STR = ["1kB", "2kB", "4kB", "8kB", "16kB", "32kB"]

ROOT_DIR = Path(__file__).resolve().parent.parent

CPUS = {
    "A7": ROOT_DIR / "m5out_A7",
    "A15": ROOT_DIR / "m5out_A15",
}

APPS = {
    "dijkstra": "size_",
    "blowfish": "blowfish_size_",
}


stats_cache = {}


def parse_stats(stats_file):
    if not os.path.exists(stats_file):
        return {}

    stats = {}
    with open(stats_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("----"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            key, value = parts[0], parts[1]
            try:
                stats[key] = float(value)
            except ValueError:
                continue
    return stats


def get_stats(stats_path):
    if stats_path not in stats_cache:
        stats_cache[stats_path] = parse_stats(stats_path)
    return stats_cache[stats_path]


def get_stat(stats, keys):
    for key in keys:
        if key in stats:
            return stats[key]
    return None


def get_ipc(stats):
    return get_stat(stats, ["system.cpu.ipc", "system.cpu.commitStats0.ipc"])


def get_sim_seconds(stats):
    value = get_stat(stats, ["simSeconds"])
    if value is not None:
        return value
    ticks = get_stat(stats, ["simTicks"])
    freq = get_stat(stats, ["simFreq"])
    if ticks is None or freq in (None, 0):
        return None
    return ticks / freq


def get_miss_rate(stats, direct_keys, hit_keys, miss_keys):
    rate = get_stat(stats, direct_keys)
    if rate is not None:
        return rate
    hits = get_stat(stats, hit_keys)
    misses = get_stat(stats, miss_keys)
    if hits is None or misses is None:
        return None
    total = hits + misses
    if total == 0:
        return None
    return misses / total


def collect_metric_by_app_cpu(metric_fn):
    data = {app: {} for app in APPS}
    for app, prefix in APPS.items():
        for cpu, base_dir in CPUS.items():
            x_vals = []
            y_vals = []
            for i, size in enumerate(SIZES_STR):
                folder_path = base_dir / f"{prefix}{size}"
                stats_path = folder_path / "stats.txt"
                stats = get_stats(stats_path)
                if not stats:
                    continue
                value = metric_fn(stats)
                if value is None:
                    continue
                x_vals.append(SIZES_KB[i])
                y_vals.append(value)
            if x_vals:
                data[app][cpu] = (x_vals, y_vals)
    return data


def plot_metric_by_app(title_prefix, y_label, out_name, metric_fn, pct=False):
    data = collect_metric_by_app_cpu(metric_fn)
    for app in APPS:
        series = data.get(app, {})
        if not series:
            print(f"No data for {title_prefix} ({app}).")
            continue

        plt.figure(figsize=(10, 6), dpi=150)

        colors = {"A7": "#1f77b4", "A15": "#d62728"}
        marker = "o"
        linestyle = "-"

        for cpu in ["A7", "A15"]:
            if cpu not in series:
                continue
            x, y = series[cpu]
            if pct:
                y = [v * 100 for v in y]
            plt.plot(
                x,
                y,
                marker=marker,
                linestyle=linestyle,
                linewidth=2,
                color=colors[cpu],
                label=cpu,
            )

        plt.title(f"{title_prefix} ({app})", fontsize=14)
        plt.xlabel("Cache Size (kB)", fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.grid(True, which="both", linestyle="--", alpha=0.7)
        plt.legend(fontsize=11)
        plt.xscale("log", base=2)
        plt.xticks(SIZES_KB, SIZES_STR)
        plt.tight_layout()

        out_path = out_name.format(app=app)
        plt.savefig(out_path)
        plt.close()


def plot_ipc(out_dir: Path):
    out_name = out_dir / "plot_comparations_ipc_{app}.png"
    plot_metric_by_app(
        "Impact of Cache Size on IPC",
        "IPC (Instructions per Cycle)",
        out_name.as_posix(),
        get_ipc,
        pct=False,
    )


def plot_exec_time(out_dir: Path):
    out_name = out_dir / "plot_comparations_time_{app}.png"
    plot_metric_by_app(
        "Execution Time vs Cache Size",
        "Simulated time (s)",
        out_name.as_posix(),
        get_sim_seconds,
        pct=False,
    )


def plot_miss_rates(out_dir: Path):
    out_l1d = out_dir / "plot_comparations_l1d_miss_{app}.png"
    out_l1i = out_dir / "plot_comparations_l1i_miss_{app}.png"
    out_l2 = out_dir / "plot_comparations_l2_miss_{app}.png"

    plot_metric_by_app(
        "L1D Miss Rate",
        "Miss rate (%)",
        out_l1d.as_posix(),
        lambda stats: get_miss_rate(
            stats,
            [
                "system.cpu.dcache.overallMissRate::total",
                "system.cpu.dcache.demandMissRate::total",
            ],
            ["system.cpu.dcache.overallHits::total"],
            ["system.cpu.dcache.overallMisses::total"],
        ),
        pct=True,
    )

    plot_metric_by_app(
        "L1I Miss Rate",
        "Miss rate (%)",
        out_l1i.as_posix(),
        lambda stats: get_miss_rate(
            stats,
            [
                "system.cpu.icache.overallMissRate::total",
                "system.cpu.icache.demandMissRate::total",
            ],
            ["system.cpu.icache.overallHits::total"],
            ["system.cpu.icache.overallMisses::total"],
        ),
        pct=True,
    )

    plot_metric_by_app(
        "L2 Miss Rate",
        "Miss rate (%)",
        out_l2.as_posix(),
        lambda stats: get_miss_rate(
            stats,
            [
                "system.l2.overallMissRate::total",
                "system.l2cache.overallMissRate::total",
                "system.l2c.overallMissRate::total",
            ],
            [
                "system.l2.overallHits::total",
                "system.l2cache.overallHits::total",
                "system.l2c.overallHits::total",
            ],
            [
                "system.l2.overallMisses::total",
                "system.l2cache.overallMisses::total",
                "system.l2c.overallMisses::total",
            ],
        ),
        pct=True,
    )


def get_branch_density(stats):
    control = get_stat(stats, ["system.cpu.commitStats0.committedControl::IsControl"])
    if control is not None:
        total_insts = get_stat(stats, ["system.cpu.commitStats0.numInsts"])
        if total_insts and total_insts > 0:
            return (control / total_insts) * 100
    return None


def get_conditional_branches(stats):
    cond = get_stat(stats, ["system.cpu.commitStats0.committedControl::IsCondControl"])
    uncond = get_stat(stats, ["system.cpu.commitStats0.committedControl::IsUncondControl"])
    if cond is not None and uncond is not None:
        total = cond + uncond
        if total > 0:
            return (cond / total) * 100
    return None


def plot_branch_analysis(out_dir: Path):
    out_density = out_dir / "plot_comparations_branch_density_{app}.png"
    out_cond = out_dir / "plot_comparations_branch_conditional_{app}.png"

    plot_metric_by_app(
        "Control Flow Density (Control instructions as % of total)",
        "Control instructions (%)",
        out_density.as_posix(),
        get_branch_density,
        pct=False,
    )

    plot_metric_by_app(
        "Conditional vs Unconditional Branches",
        "Conditional branches (%)",
        out_cond.as_posix(),
        get_conditional_branches,
        pct=False,
    )


def print_summary():
    print("=" * 80)
    print("RESUMO DE METRICAS DISPONIVEIS NOS DADOS")
    print("=" * 80)
    print()

    for app, prefix in APPS.items():
        for cpu, base_dir in CPUS.items():
            label = f"{cpu} - {app.capitalize()}"
            print(f"\n{label}:")
            print("-" * 50)

            for size in SIZES_STR:
                folder_path = base_dir / f"{prefix}{size}"
                stats_path = folder_path / "stats.txt"
                stats = get_stats(stats_path)

                if not stats:
                    print(f"  {size}: [SEM DADOS]")
                    continue

                ipc = get_ipc(stats)
                sim_time = get_sim_seconds(stats)
                dcache_miss = get_miss_rate(
                    stats,
                    ["system.cpu.dcache.overallMissRate::total"],
                    ["system.cpu.dcache.overallHits::total"],
                    ["system.cpu.dcache.overallMisses::total"],
                )
                icache_miss = get_miss_rate(
                    stats,
                    ["system.cpu.icache.overallMissRate::total"],
                    ["system.cpu.icache.overallHits::total"],
                    ["system.cpu.icache.overallMisses::total"],
                )

                if ipc is None or sim_time is None or dcache_miss is None or icache_miss is None:
                    print(f"  {size}: [DADOS INCOMPLETOS]")
                    continue

                print(
                    f"  {size:>4}: IPC={ipc:.4f} | Time={sim_time:.4f}s | "
                    f"L1D-Miss={dcache_miss * 100:.1f}% | L1I-Miss={icache_miss * 100:.1f}%"
                )


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "plots"
    out_dir.mkdir(parents=True, exist_ok=True)

    plot_ipc(out_dir)
    plot_exec_time(out_dir)
    plot_miss_rates(out_dir)
    plot_branch_analysis(out_dir)
    print_summary()


if __name__ == "__main__":
    main()
