# TP4 - Ex4 - Q10/Q11 (Efficacite energetique)

## Q4/Q5 (Performance)

Parametres et entrees utilises (gem5) :
- Script d'execution : [ES201-TP/TP4/ex4/script_ex4.sh](ES201-TP/TP4/ex4/script_ex4.sh)
- Configuration A7 : [ES201-TP/TP4/ex4/se_A7.py](ES201-TP/TP4/ex4/se_A7.py)
- Configuration A15 : [ES201-TP/TP4/ex4/se_A15.py](ES201-TP/TP4/ex4/se_A15.py)
- Dijkstra : dijkstra_small.riscv + input.dat
- Blowfish : bf.riscv + input.dat
- L2 fixe : 512kB
- L1 A7 : 1, 2, 4, 8, 16 kB
- L1 A15 : 2, 4, 8, 16, 32 kB

Explication du flux de simulation :
- Compilation des binaires RISC-V (Dijkstra/Blowfish), puis execution via gem5 en mode SE.
- Pour chaque taille de L1, lancement de gem5 avec les configs A7 ou A15 et collecte des stats dans m5out_*.
- Extraction des metriques (IPC, CPI, miss rates, etc.) a partir des stats.txt et generation des graphes.

Formule du nombre de sets (nsets) :
$$
	ext{nsets} = \frac{\text{taille du cache}}{\text{taille du bloc} \times \text{associativite}}
$$
Exemple L2 : taille 512KB, bloc 64B, associativite 16 -> nsets = 512.

Parametres principaux (gem5) utilises dans les configurations :
- A7 : line size 32B, fetch buffer 32B, fetch queue 8
- A7 : decode/issue/commit = 2/4/2, fetch/rename/dispatch/wb = 2/4/4/2
- A7 : ROB/LQ/SQ = 2/8/8, branch predictor BiMode, BTB=256
- A7 : L1I/L1D assoc=2, L2 assoc=8
- A15 : line size 64B, fetch queue 15
- A15 : decode/issue/commit = 4/8/4, fetch/rename/dispatch/wb = 4/8/8/4
- A15 : ROB/LQ/SQ = 16/16/16, branch predictor LocalBP (2-level), BTB=256
- A15 : L1I/L1D assoc=2, L2 assoc=16

### Dijkstra (CPI)

| L1 size | CPU | CPI |
|---|---|---:|
| 1kB | A7 | 4.173012 |
| 2kB | A7 | 3.998006 |
| 4kB | A7 | 3.832790 |
| 8kB | A7 | 3.569464 |
| 16kB | A7 | 3.488448 |
| 2kB | A15 | 1.479224 |
| 4kB | A15 | 1.352008 |
| 8kB | A15 | 1.089098 |
| 16kB | A15 | 1.013689 |
| 32kB | A15 | 0.901460 |

### Blowfish (CPI)

| L1 size | CPU | CPI |
|---|---|---:|
| 1kB | A7 | 12.416576 |
| 2kB | A7 | 12.318750 |
| 4kB | A7 | 12.122283 |
| 8kB | A7 | 12.037908 |
| 16kB | A7 | 11.968614 |
| 2kB | A15 | 6.470788 |
| 4kB | A15 | 6.285870 |
| 8kB | A15 | 6.188179 |
| 16kB | A15 | 6.163451 |
| 32kB | A15 | 6.128533 |

Conclusions (Q4/Q5) :
- Dijkstra : IPC augmente et CPI baisse avec un L1 plus grand ; meilleur L1 observe = 16kB (A7) et 32kB (A15).
- Blowfish : IPC evolue peu ; gains marginaux apres 8kB ; meilleur L1 observe = 16kB (A7) et 32kB (A15).

## Q10

Donnees :
- A7 : 0.10 mW/MHz, fmax = 1.0 GHz = 1000 MHz
- A15 : 0.20 mW/MHz, fmax = 2.5 GHz = 2500 MHz

Puissance a fmax :
- Cortex A7 : 0.10 x 1000 = 100 mW
- Cortex A15 : 0.20 x 2500 = 500 mW

## Q11

Formule :
- Efficacite energetique = IPC / consommation (mW)

Note d'unite : pour comparer avec des tableaux en IPC/W, multiplier les valeurs par 1000.

IPC extrait de :
- A7 : m5out_A7/*/stats.txt (system.cpu.ipc)
- A15 : m5out_A15/*/stats.txt (system.cpu.ipc)

Analyse rapide :
- Sur dijkstra, l'efficacite augmente avec un L1 plus grand sur les deux CPUs, mais A7 reste plus efficace (max A7 0.002867 vs max A15 0.002219).
- Sur blowfish, les gains avec L1 sont faibles et A7 reste plus efficace sur toute la plage testee.
- A15 progresse plus avec L1, mais la consommation 5x domine le resultat.

### Dijkstra

| L1 size | CPU | IPC | Power (mW) | Efficiency (IPC/mW) |
|---|---|---:|---:|---:|
| 1kB | A7 | 0.239635 | 100 | 0.002396 |
| 2kB | A7 | 0.250125 | 100 | 0.002501 |
| 4kB | A7 | 0.260907 | 100 | 0.002609 |
| 8kB | A7 | 0.280154 | 100 | 0.002802 |
| 16kB | A7 | 0.286660 | 100 | 0.002867 |
| 2kB | A15 | 0.676030 | 500 | 0.001352 |
| 4kB | A15 | 0.739640 | 500 | 0.001479 |
| 8kB | A15 | 0.918191 | 500 | 0.001836 |
| 16kB | A15 | 0.986496 | 500 | 0.001973 |
| 32kB | A15 | 1.109311 | 500 | 0.002219 |

### Tableaux par CPU (IPC/mW)

#### A7 - Dijkstra

| L1 size | IPC | Efficiency (IPC/mW) |
|---|---:|---:|
| 1kB | 0.239635 | 0.002396 |
| 2kB | 0.250125 | 0.002501 |
| 4kB | 0.260907 | 0.002609 |
| 8kB | 0.280154 | 0.002802 |
| 16kB | 0.286660 | 0.002867 |

#### A7 - Blowfish

| L1 size | IPC | Efficiency (IPC/mW) |
|---|---:|---:|
| 1kB | 0.080538 | 0.000805 |
| 2kB | 0.081177 | 0.000812 |
| 4kB | 0.082493 | 0.000825 |
| 8kB | 0.083071 | 0.000831 |
| 16kB | 0.083552 | 0.000836 |

#### A15 - Dijkstra

| L1 size | IPC | Efficiency (IPC/mW) |
|---|---:|---:|
| 2kB | 0.676030 | 0.001352 |
| 4kB | 0.739640 | 0.001479 |
| 8kB | 0.918191 | 0.001836 |
| 16kB | 0.986496 | 0.001973 |
| 32kB | 1.109311 | 0.002219 |

#### A15 - Blowfish

| L1 size | IPC | Efficiency (IPC/mW) |
|---|---:|---:|
| 2kB | 0.154541 | 0.000309 |
| 4kB | 0.159087 | 0.000318 |
| 8kB | 0.161598 | 0.000323 |
| 16kB | 0.162247 | 0.000324 |
| 32kB | 0.163171 | 0.000326 |

### Blowfish

| L1 size | CPU | IPC | Power (mW) | Efficiency (IPC/mW) |
|---|---|---:|---:|---:|
| 1kB | A7 | 0.080538 | 100 | 0.000805 |
| 2kB | A7 | 0.081177 | 100 | 0.000812 |
| 4kB | A7 | 0.082493 | 100 | 0.000825 |
| 8kB | A7 | 0.083071 | 100 | 0.000831 |
| 16kB | A7 | 0.083552 | 100 | 0.000836 |
| 2kB | A15 | 0.154541 | 500 | 0.000309 |
| 4kB | A15 | 0.159087 | 500 | 0.000318 |
| 8kB | A15 | 0.161598 | 500 | 0.000323 |
| 16kB | A15 | 0.162247 | 500 | 0.000324 |
| 32kB | A15 | 0.163171 | 500 | 0.000326 |

## Graphiques

![Dijkstra - eficiencia energetica](plots/dijkstra_energy_efficiency.png)

![Blowfish - eficiencia energetica](plots/blowfish_energy_efficiency.png)

## Comparaison par CPU

![A7 - Dijkstra vs Blowfish](plots/a7_energy_efficiency_by_app.png)

![A15 - Dijkstra vs Blowfish](plots/a15_energy_efficiency_by_app.png)

## Comparaisons detaillees

### Dijkstra

![IPC vs L1 - Dijkstra](plots/plot_comparations_ipc_dijkstra.png)

![Tempo de execucao vs L1 - Dijkstra](plots/plot_comparations_time_dijkstra.png)

![L1D miss - Dijkstra](plots/plot_comparations_l1d_miss_dijkstra.png)

![L1I miss - Dijkstra](plots/plot_comparations_l1i_miss_dijkstra.png)

![L2 miss - Dijkstra](plots/plot_comparations_l2_miss_dijkstra.png)

![Branch density - Dijkstra](plots/plot_comparations_branch_density_dijkstra.png)

![Conditional branches - Dijkstra](plots/plot_comparations_branch_conditional_dijkstra.png)

### Blowfish

![IPC vs L1 - Blowfish](plots/plot_comparations_ipc_blowfish.png)

![Tempo de execucao vs L1 - Blowfish](plots/plot_comparations_time_blowfish.png)

![L1D miss - Blowfish](plots/plot_comparations_l1d_miss_blowfish.png)

![L1I miss - Blowfish](plots/plot_comparations_l1i_miss_blowfish.png)

![L2 miss - Blowfish](plots/plot_comparations_l2_miss_blowfish.png)

![Branch density - Blowfish](plots/plot_comparations_branch_density_blowfish.png)

![Conditional branches - Blowfish](plots/plot_comparations_branch_conditional_blowfish.png)
