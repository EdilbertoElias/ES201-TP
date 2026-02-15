#!/usr/bin/env bash
set -euo pipefail

# --------- CHEMINS A ADAPTER ----------
GEM5="/home/edilberto-elias-xavier-junior/gem5/build/RISCV/gem5.opt" # chemin vers le binaire de gem5
CFG="/home/edilberto-elias-xavier-junior/Informatique/Architecture/ES201-TP/TP4/ex4" # chemin vers le script de configuration de la simulation

BIN_DIR="/home/edilberto-elias-xavier-junior/Informatique/Architecture/ES201-TP/TP4/Projet/"   # là où sont les .riscv
# ------------------------------------------

mkdir -p m5out_A7 m5out_A15 # répertoires de sortie pour les résultats des simulations

BENCH_NAME="dijkstra_small.riscv" # nom du binaire à simuler (doit être présent dans BIN_DIR)
BENCH_ARGS="$BIN_DIR/dijkstra/input.dat" # arguments à passer au binaire lors de la simulation (ex: "input.dat" pour dijkstra_small.riscv)

BENCH_BIN="$BIN_DIR/dijkstra/$BENCH_NAME"

# --------- SIMULATIONS A7 ----------
echo "Simulating A7 for dijkstra..."

for size_cache in "1kB" "2kB" "4kB" "8kB" "16kB"; do # on teste différentes tailles de cache L1
    echo "Simulating A7 with cache size: $size_cache for dijkstra..."
    OUT_DIR="m5out_A7/dijkstra_size_${size_cache}" # répertoire de sortie spécifique pour cette configuration de cache
    mkdir -p "$OUT_DIR" # on crée le répertoire de sortie s'il n'existe pas

    $GEM5 -d "$OUT_DIR" "$CFG/se_A7.py" \
        --cmd=$BENCH_BIN \
        --options="$BENCH_ARGS" \
        --caches="$size_cache" > /dev/null 2>&1

done

# --------- SIMULATIONS A15 ----------
echo "Simulating A15 for dijkstra..."

for size_cache in "2kB" "4kB" "8kB" "16kB" "32kB"; do
    echo "Simulating A15 with cache size: $size_cache for dijkstra..."
    OUT_DIR="m5out_A15/dijkstra_size_${size_cache}"
    mkdir -p "$OUT_DIR"

    $GEM5 -d "$OUT_DIR" "$CFG/se_A15.py" \
        --cmd=$BENCH_BIN \
        --options="$BENCH_ARGS" \
        --caches="$size_cache" > /dev/null 2>&1

done

BENCH_NAME="bf.riscv" # nom du binaire à simuler (doit être présent dans BIN_DIR)
BENCH_ARGS="$BIN_DIR/blowfish/input.dat" # arguments à passer au binaire lors de la simulation (ex: "input.dat" pour bf.riscv)

BENCH_BIN="$BIN_DIR/blowfish/$BENCH_NAME"

# --------- SIMULATIONS A7 ----------
echo "Simulating A7 for blowfish..."

for size_cache in "1kB" "2kB" "4kB" "8kB" "16kB"; do
    echo "Simulating A7 with cache size: $size_cache for blowfish..."
    OUT_DIR="m5out_A7/blowfish_size_${size_cache}"
    mkdir -p "$OUT_DIR"

    $GEM5 -d "$OUT_DIR" "$CFG/se_A7.py" \
        --cmd=$BENCH_BIN \
        --options="$BENCH_ARGS" \
        --caches="$size_cache" > /dev/null 2>&1

done

# --------- SIMULATIONS A15 ----------
echo "Simulating A15 for blowfish..."

for size_cache in "2kB" "4kB" "8kB" "16kB" "32kB"; do
    echo "Simulating A15 with cache size: $size_cache for blowfish..."
    OUT_DIR="m5out_A15/blowfish_size_${size_cache}"
    mkdir -p "$OUT_DIR"

    $GEM5 -d "$OUT_DIR" "$CFG/se_A15.py" \
        --cmd=$BENCH_BIN \
        --options="$BENCH_ARGS" \
        --caches="$size_cache" > /dev/null 2>&1

done